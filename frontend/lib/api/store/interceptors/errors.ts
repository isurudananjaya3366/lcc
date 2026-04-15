import { AxiosError, AxiosInstance, AxiosResponse } from 'axios';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ApiErrorResponse {
  error?: string;
  message?: string;
  details?: string;
  field_errors?: Record<string, string[]>;
  timestamp?: string;
  request_id?: string;
}

export interface TransformedError {
  title: string;
  message: string;
  statusCode: number;
  isRetryable: boolean;
  fieldErrors?: Record<string, string[]>;
  originalError: AxiosError;
}

export interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryableStatuses: number[];
  backoffMultiplier: number;
}

// ─── Constants ──────────────────────────────────────────────────────────────

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryableStatuses: [408, 429, 500, 502, 503],
  backoffMultiplier: 2,
};

const STATUS_MESSAGES: Record<number, { title: string; message: string }> = {
  400: { title: 'Bad Request', message: 'Invalid request. Please check your input.' },
  401: { title: 'Unauthorized', message: 'Please log in to continue.' },
  403: { title: 'Forbidden', message: "You don't have permission to access this resource." },
  404: { title: 'Not Found', message: 'The requested item was not found.' },
  409: { title: 'Conflict', message: 'This item already exists.' },
  422: { title: 'Validation Error', message: 'Please fix the errors and try again.' },
  429: { title: 'Too Many Requests', message: 'Too many requests. Please wait a moment.' },
  500: { title: 'Server Error', message: 'Server error. Please try again later.' },
  502: { title: 'Service Unavailable', message: 'Service temporarily unavailable.' },
  503: { title: 'Service Unavailable', message: 'Service temporarily unavailable.' },
};

const IDEMPOTENT_METHODS = ['get', 'head', 'put', 'delete', 'options'];

// ─── Error Type Detection ───────────────────────────────────────────────────

export function isNetworkError(error: AxiosError): boolean {
  return !error.response && !!error.request;
}

export function isServerError(error: AxiosError): boolean {
  return (error.response?.status ?? 0) >= 500;
}

export function isClientError(error: AxiosError): boolean {
  const status = error.response?.status ?? 0;
  return status >= 400 && status < 500;
}

export function isTimeoutError(error: AxiosError): boolean {
  return error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT';
}

// ─── Error Processing ───────────────────────────────────────────────────────

export function parseErrorResponse(error: AxiosError<ApiErrorResponse>): TransformedError {
  const status = error.response?.status ?? 0;
  const data = error.response?.data;

  const statusMessage = STATUS_MESSAGES[status] ?? {
    title: 'Error',
    message: 'An unexpected error occurred.',
  };

  let message = statusMessage.message;
  if (data?.message) {
    message = data.message;
  } else if (data?.error) {
    message = data.error;
  } else if (data?.details) {
    message = data.details;
  }

  if (isNetworkError(error)) {
    return {
      title: 'Network Error',
      message: 'Unable to connect. Please check your internet connection.',
      statusCode: 0,
      isRetryable: true,
      originalError: error,
    };
  }

  if (isTimeoutError(error)) {
    return {
      title: 'Request Timeout',
      message: 'The request took too long. Please try again.',
      statusCode: 408,
      isRetryable: true,
      originalError: error,
    };
  }

  return {
    title: statusMessage.title,
    message,
    statusCode: status,
    isRetryable: DEFAULT_RETRY_CONFIG.retryableStatuses.includes(status),
    fieldErrors: data?.field_errors,
    originalError: error,
  };
}

export function getUserMessage(error: AxiosError<ApiErrorResponse>): string {
  return parseErrorResponse(error).message;
}

// ─── Retry Logic ────────────────────────────────────────────────────────────

export function shouldRetry(error: AxiosError, retryCount: number): boolean {
  if (retryCount >= DEFAULT_RETRY_CONFIG.maxRetries) return false;

  const method = error.config?.method?.toLowerCase() ?? '';
  if (!IDEMPOTENT_METHODS.includes(method) && method !== 'post') return false;

  if (isNetworkError(error) || isTimeoutError(error)) return true;

  const status = error.response?.status ?? 0;
  return DEFAULT_RETRY_CONFIG.retryableStatuses.includes(status);
}

export function calculateBackoff(retryCount: number): number {
  const delay =
    DEFAULT_RETRY_CONFIG.retryDelay * Math.pow(DEFAULT_RETRY_CONFIG.backoffMultiplier, retryCount);
  const jitter = Math.random() * 1000;
  return Math.min(delay + jitter, 30000);
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Error Logging ──────────────────────────────────────────────────────────

function logError(error: AxiosError<ApiErrorResponse>, context: string): void {
  if (process.env.NODE_ENV === 'development') {
    console.error(`[Store API] ${context}:`, {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: getUserMessage(error),
    });
  }
}

// ─── Interceptor Setup ─────────────────────────────────────────────────────

export function setupErrorInterceptor(instance: AxiosInstance): void {
  instance.interceptors.response.use(
    (response: AxiosResponse) => response,
    async (error: AxiosError<ApiErrorResponse>) => {
      const config = error.config as InternalRetryConfig | undefined;
      if (!config) return Promise.reject(parseErrorResponse(error));

      // Initialize retry count
      if (config.__retryCount === undefined) {
        config.__retryCount = 0;
      }

      logError(error, `Request failed (attempt ${config.__retryCount + 1})`);

      // Retry if applicable
      if (shouldRetry(error, config.__retryCount)) {
        config.__retryCount += 1;
        const delay = calculateBackoff(config.__retryCount);

        if (process.env.NODE_ENV === 'development') {
          console.log(
            `[Store API] Retrying in ${Math.round(delay)}ms (attempt ${config.__retryCount}/${DEFAULT_RETRY_CONFIG.maxRetries})`
          );
        }

        await sleep(delay);
        return instance.request(config);
      }

      return Promise.reject(parseErrorResponse(error));
    }
  );
}

// Internal type for retry tracking
interface InternalRetryConfig extends Record<string, unknown> {
  __retryCount?: number;
  url?: string;
  method?: string;
}
