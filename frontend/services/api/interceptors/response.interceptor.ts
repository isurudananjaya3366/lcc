/**
 * Response Interceptors
 *
 * Processes all API responses:
 * - Extracts data from successful responses
 * - Handles 401 with token refresh queue
 * - Handles 403, 404, 422, 5xx errors with typed error objects
 * - Logs response timing in development
 */

import type { AxiosError, AxiosInstance, AxiosResponse } from 'axios';
import { getRefreshToken, setAccessToken, clearTokens } from '@/lib/tokenStorage';

// ── Token Refresh Queue (Task 43) ─────────────────────────────

let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

function subscribeTokenRefresh(callback: (token: string) => void): void {
  refreshSubscribers.push(callback);
}

function notifySubscribers(token: string): void {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function resetRefreshState(): void {
  isRefreshing = false;
  refreshSubscribers = [];
}

// ── Success Handler (Task 37) ──────────────────────────────────

/**
 * Handle successful responses (200-299).
 *
 * Returns the full AxiosResponse so callers can destructure `{ data }` as
 * well as access `headers` (pagination) and `status`.  Nested `{ data: … }`
 * unwrapping happens at the data level: if `response.data` itself contains a
 * single `data` key, the inner value is promoted.
 */
export function responseSuccessHandler(response: AxiosResponse): AxiosResponse {
  // Log response time (Task 44)
  if (process.env.NODE_ENV === 'development') {
    const meta = (response.config as any).metadata;
    if (meta?.startPerformance && typeof performance !== 'undefined') {
      const duration = (performance.now() - meta.startPerformance).toFixed(2);
      console.log(
        `[API] ✓ ${response.config.method?.toUpperCase()} ${response.config.url}`,
        `${response.status} (${duration}ms)`
      );
    }
  }

  // Handle nested data structures — if backend wraps in { data: {...} }
  const payload = response.data;
  if (
    payload &&
    typeof payload === 'object' &&
    !Array.isArray(payload) &&
    'data' in payload &&
    Object.keys(payload).length === 1
  ) {
    response.data = payload.data;
  }

  return response;
}

// ── Error Handler (Tasks 38-42) ────────────────────────────────

export function createResponseErrorHandler(axiosInstance: AxiosInstance) {
  return async (error: AxiosError): Promise<never> => {
    // Log response time even for errors (Task 44)
    if (process.env.NODE_ENV === 'development') {
      const meta = (error.config as any)?.metadata;
      if (meta?.startPerformance && typeof performance !== 'undefined') {
        const duration = (performance.now() - meta.startPerformance).toFixed(2);
        console.log(
          `[API] ✗ ${error.config?.method?.toUpperCase()} ${error.config?.url}`,
          `${error.response?.status || 'NETWORK'} (${duration}ms)`
        );
      }
    }

    const status = error.response?.status;

    switch (status) {
      case 401:
        return handle401(error, axiosInstance);
      case 403:
        return handle403(error);
      case 404:
        return handle404(error);
      case 400:
      case 422:
        return handle422(error);
      case 500:
      case 502:
      case 503:
      case 504:
        return handle5xx(error);
      default:
        return Promise.reject(error);
    }
  };
}

// ── 401 Unauthorized (Task 38 + Task 43 queue) ─────────────────

async function handle401(error: AxiosError, axiosInstance: AxiosInstance): Promise<never> {
  const originalRequest = error.config as any;

  // Don't retry refresh endpoint itself
  if (originalRequest?.url?.includes('/auth/refresh')) {
    clearTokens();
    return Promise.reject(error);
  }

  // Prevent infinite retry loops
  if (originalRequest?._retry) {
    clearTokens();
    return Promise.reject(error);
  }

  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    return Promise.reject(error);
  }

  originalRequest._retry = true;

  // If refresh is already in progress, queue this request
  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      subscribeTokenRefresh((token: string) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        resolve(axiosInstance(originalRequest) as any);
      });
    });
  }

  isRefreshing = true;

  try {
    const response = await axiosInstance.post('/auth/refresh', {
      refreshToken,
    });
    const newToken = response.data?.accessToken || response.data;
    setAccessToken(newToken);
    originalRequest.headers.Authorization = `Bearer ${newToken}`;
    notifySubscribers(newToken);
    return axiosInstance(originalRequest) as unknown as Promise<never>;
  } catch {
    clearTokens();
    return Promise.reject(error);
  } finally {
    resetRefreshState();
  }
}

// ── 403 Forbidden (Task 39) ────────────────────────────────────

function handle403(error: AxiosError): Promise<never> {
  const responseData = error.response?.data as any;
  const message =
    responseData?.message ||
    responseData?.detail ||
    "You don't have permission to access this resource";

  const permissionError: any = new Error(message);
  permissionError.type = 'PermissionError';
  permissionError.statusCode = 403;
  permissionError.resource = error.config?.url;
  permissionError.method = error.config?.method?.toUpperCase();
  permissionError.timestamp = new Date();

  if (process.env.NODE_ENV === 'development') {
    console.warn('[API] Permission Denied:', error.config?.url);
  }

  return Promise.reject(permissionError);
}

// ── 404 Not Found (Task 40) ───────────────────────────────────

function handle404(error: AxiosError): Promise<never> {
  const url = error.config?.url || '';
  const urlParts = url.split('/').filter(Boolean);
  const resourceType = urlParts[urlParts.length - 2] || 'resource';
  const resourceId = urlParts[urlParts.length - 1];

  const notFoundError: any = new Error(`The ${resourceType.replace(/s$/, '')} was not found`);
  notFoundError.type = 'NotFoundError';
  notFoundError.statusCode = 404;
  notFoundError.resource = url;
  notFoundError.resourceType = resourceType.replace(/s$/, '');
  notFoundError.resourceId = resourceId;
  notFoundError.method = error.config?.method?.toUpperCase();
  notFoundError.timestamp = new Date();

  if (process.env.NODE_ENV === 'development') {
    console.warn('[API] Not Found:', url);
  }

  return Promise.reject(notFoundError);
}

// ── 422 Validation Errors (Task 41) ───────────────────────────

function handle422(error: AxiosError): Promise<never> {
  const responseData = error.response?.data as any;
  const fieldErrors: Record<string, string[]> = {};
  const nonFieldErrors: string[] = [];

  if (responseData && typeof responseData === 'object') {
    for (const [key, value] of Object.entries(responseData)) {
      if (key === 'non_field_errors' || key === '_errors' || key === 'general') {
        if (Array.isArray(value)) {
          nonFieldErrors.push(...(value as string[]));
        } else if (typeof value === 'string') {
          nonFieldErrors.push(value);
        }
      } else if (Array.isArray(value)) {
        fieldErrors[key] = value as string[];
      } else if (typeof value === 'string') {
        fieldErrors[key] = [value];
      }
    }
  }

  const validationError: any = new Error('Validation failed');
  validationError.type = 'ValidationError';
  validationError.statusCode = error.response?.status || 422;
  validationError.fieldErrors = fieldErrors;
  validationError.nonFieldErrors = nonFieldErrors;
  validationError.timestamp = new Date();
  validationError.getFieldError = (field: string) => fieldErrors[field] || [];
  validationError.getAllMessages = () => [...nonFieldErrors, ...Object.values(fieldErrors).flat()];
  validationError.getFirstError = (field: string) => fieldErrors[field]?.[0];
  validationError.hasFieldError = (field: string) => !!fieldErrors[field];

  if (process.env.NODE_ENV === 'development') {
    console.warn('[API] Validation Error:', fieldErrors);
  }

  return Promise.reject(validationError);
}

// ── 5xx Server Errors (Task 42) ───────────────────────────────

function handle5xx(error: AxiosError): Promise<never> {
  const status = error.response?.status;
  const responseData = error.response?.data as any;

  const message = responseData?.message || getDefaultServerErrorMessage(status);

  const serverError: any = new Error(message);
  serverError.type = 'ServerError';
  serverError.statusCode = status;
  serverError.errorId = responseData?.error_id || responseData?.id;
  serverError.resource = error.config?.url;
  serverError.method = error.config?.method?.toUpperCase();
  serverError.timestamp = new Date();
  serverError.retryable = [502, 503, 504].includes(status!);

  console.error(`[API] Server Error ${status}:`, error.config?.url);

  return Promise.reject(serverError);
}

function getDefaultServerErrorMessage(status?: number): string {
  switch (status) {
    case 502:
      return 'Service temporarily unavailable. Please try again.';
    case 503:
      return 'Service is under maintenance. Please try again later.';
    case 504:
      return 'Request timed out. Please try again.';
    default:
      return 'Something went wrong. Please try again.';
  }
}
