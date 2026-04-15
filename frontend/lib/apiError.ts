/**
 * API Error Handling Module
 *
 * Provides the ApiException class, error parsing utilities,
 * retry logic with exponential backoff, request cancellation,
 * and offline detection for resilient API communication.
 */

import { isAxiosError } from 'axios';
import type { AxiosError } from 'axios';

// ── Types ──────────────────────────────────────────────────────

export interface ApiErrorDetails {
  [field: string]: string[];
}

export interface RetryConfig {
  maxRetries: number;
  initialDelay: number;
  maxDelay: number;
  backoffFactor: number;
  retryCondition?: (error: ApiException) => boolean;
}

export const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelay: 1000,
  maxDelay: 10000,
  backoffFactor: 2,
};

// ── ApiException Class (Task 46) ───────────────────────────────

export class ApiException extends Error {
  code: string;
  status: number;
  details: ApiErrorDetails | null;
  isNetworkError: boolean;
  isTimeoutError: boolean;
  isCancelled: boolean;
  originalError?: unknown;

  constructor(
    message: string,
    options?: {
      code?: string;
      status?: number;
      details?: ApiErrorDetails;
      isNetworkError?: boolean;
      isTimeoutError?: boolean;
      isCancelled?: boolean;
      originalError?: unknown;
    }
  ) {
    super(message);
    this.name = 'ApiException';
    this.code = options?.code ?? 'UNKNOWN';
    this.status = options?.status ?? 0;
    this.details = options?.details ?? null;
    this.isNetworkError = options?.isNetworkError ?? false;
    this.isTimeoutError = options?.isTimeoutError ?? false;
    this.isCancelled = options?.isCancelled ?? false;
    this.originalError = options?.originalError;
    Object.setPrototypeOf(this, ApiException.prototype);
  }

  static fromAxiosError(error: AxiosError): ApiException {
    return parseApiError(error);
  }

  static networkError(message = 'Network connection failed'): ApiException {
    return new ApiException(message, {
      code: 'NETWORK',
      isNetworkError: true,
    });
  }

  static timeoutError(message = 'Request timed out'): ApiException {
    return new ApiException(message, {
      code: 'TIMEOUT',
      isTimeoutError: true,
    });
  }

  static serverError(status: number, message = 'Server error'): ApiException {
    return new ApiException(message, { code: 'SERVER_ERROR', status });
  }

  toJSON() {
    return {
      name: this.name,
      message: this.message,
      code: this.code,
      status: this.status,
      details: this.details,
      isNetworkError: this.isNetworkError,
      isTimeoutError: this.isTimeoutError,
      isCancelled: this.isCancelled,
    };
  }
}

// ── parseApiError (Task 47) ────────────────────────────────────

export function parseApiError(error: unknown): ApiException {
  if (error instanceof ApiException) return error;

  if (isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;

    // Cancelled request
    if (axiosError.code === 'ERR_CANCELED') {
      return new ApiException('Request was cancelled', {
        code: 'CANCELLED',
        isCancelled: true,
        originalError: error,
      });
    }

    // Timeout
    if (
      axiosError.code === 'ECONNABORTED' ||
      axiosError.code === 'ETIMEDOUT' ||
      axiosError.message?.toLowerCase().includes('timeout')
    ) {
      return new ApiException('Request timed out. Please try again.', {
        code: 'TIMEOUT',
        isTimeoutError: true,
        originalError: error,
      });
    }

    // Network error (request sent but no response)
    if (axiosError.code === 'ERR_NETWORK' || (!axiosError.response && axiosError.request)) {
      return new ApiException('Unable to connect to the server. Check your internet connection.', {
        code: 'NETWORK',
        isNetworkError: true,
        originalError: error,
      });
    }

    // HTTP error with response
    if (axiosError.response) {
      const { data, status } = axiosError.response;
      const message = data?.message || data?.detail || axiosError.message || 'Request failed';
      const code = data?.code || String(status);
      const details: ApiErrorDetails | undefined = data?.errors || data?.details;

      // DRF validation format: { field: [messages] }
      let fieldErrors: ApiErrorDetails | undefined;
      if (status === 400 || status === 422) {
        fieldErrors = {};
        if (typeof data === 'object' && data !== null) {
          for (const [key, val] of Object.entries(data)) {
            if (key === 'message' || key === 'code' || key === 'detail') continue;
            if (Array.isArray(val)) {
              fieldErrors[key] = val as string[];
            } else if (typeof val === 'string') {
              fieldErrors[key] = [val];
            }
          }
        }
        if (Object.keys(fieldErrors).length === 0) fieldErrors = undefined;
      }

      return new ApiException(message, {
        code,
        status,
        details: details || fieldErrors || undefined,
        originalError: error,
      });
    }

    // Request setup error
    return new ApiException(axiosError.message || 'Request failed', {
      code: 'REQUEST_SETUP',
      originalError: error,
    });
  }

  // Standard Error
  if (error instanceof Error) {
    return new ApiException(error.message, {
      code: 'UNKNOWN',
      originalError: error,
    });
  }

  // Unknown / string / other
  return new ApiException(String(error), {
    code: 'UNKNOWN',
    originalError: error,
  });
}

// ── getErrorMessage (Task 48) ──────────────────────────────────

const STATUS_MESSAGES: Record<number, string> = {
  400: 'The request was invalid. Please check your input.',
  401: 'Your session has expired. Please log in again.',
  403: "You don't have permission to perform this action.",
  404: 'The requested resource was not found.',
  408: 'The request timed out. Please try again.',
  422: 'Please check your input and try again.',
  429: 'Too many requests. Please wait a moment and try again.',
  500: 'Something went wrong on our end. Please try again later.',
  502: 'The server is temporarily unavailable. Please try again.',
  503: 'The service is currently undergoing maintenance.',
  504: 'The request took too long. Please try again.',
};

export function getErrorMessage(error: unknown): string {
  if (!error) return 'An unexpected error occurred';
  if (typeof error === 'string') return error;

  if (error instanceof ApiException) {
    if (error.isCancelled) return 'Request was cancelled';
    if (error.isNetworkError) return 'Check your internet connection and try again.';
    if (error.isTimeoutError) return 'Request timed out. Please try again.';
    if (error.status && STATUS_MESSAGES[error.status]) {
      return STATUS_MESSAGES[error.status] ?? error.message;
    }
    return error.message || 'An unexpected error occurred';
  }

  if (error instanceof Error) {
    return error.message || 'An unexpected error occurred';
  }

  return 'An unexpected error occurred';
}

// ── isNetworkError (Task 49) ───────────────────────────────────

export function isNetworkError(error: unknown): boolean {
  if (error instanceof ApiException) return error.isNetworkError;

  if (isAxiosError(error)) {
    if (error.code === 'ERR_NETWORK') return true;
    if (error.request && !error.response) return true;
  }

  if (error instanceof Error) {
    const msg = error.message.toLowerCase();
    return (
      msg.includes('network error') ||
      msg.includes('failed to fetch') ||
      msg.includes('connection refused')
    );
  }

  return false;
}

// ── isTimeoutError (Task 50) ───────────────────────────────────

export function isTimeoutError(error: unknown): boolean {
  if (error instanceof ApiException) return error.isTimeoutError;

  if (isAxiosError(error)) {
    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') return true;
    if (error.response?.status === 408) return true;
  }

  if (error instanceof Error) {
    const msg = error.message.toLowerCase();
    return msg.includes('timeout') || msg.includes('timed out');
  }

  return false;
}

// ── isRetryable (Task 54) ──────────────────────────────────────

export function isRetryable(error: unknown): boolean {
  if (isNetworkError(error)) return true;
  if (isTimeoutError(error)) return true;

  const apiError = error instanceof ApiException ? error : parseApiError(error);

  if (apiError.isCancelled) return false;

  const { status } = apiError;
  if (status === 429) return true;
  if (status === 501) return false;
  if (status >= 500) return true;

  return false;
}

// ── calculateBackoffDelay (Task 53) ────────────────────────────

export function calculateBackoffDelay(attemptNumber: number, config: RetryConfig): number {
  const attempt = Math.max(0, attemptNumber);
  const delay = config.initialDelay * Math.pow(config.backoffFactor, attempt);
  const capped = Math.min(delay, config.maxDelay);
  // Add jitter: 50-100% of calculated delay
  return capped * (0.5 + Math.random() * 0.5);
}

// ── retryRequest (Task 52) ─────────────────────────────────────

export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  config?: Partial<RetryConfig>
): Promise<T> {
  const finalConfig = { ...DEFAULT_RETRY_CONFIG, ...config };
  let lastError: ApiException | null = null;

  for (let attempt = 0; attempt <= finalConfig.maxRetries; attempt++) {
    try {
      return await requestFn();
    } catch (err) {
      lastError = parseApiError(err);

      // Check custom retry condition first
      const shouldRetry = finalConfig.retryCondition
        ? finalConfig.retryCondition(lastError)
        : isRetryable(lastError);

      if (!shouldRetry || attempt >= finalConfig.maxRetries) {
        throw lastError;
      }

      const delay = calculateBackoffDelay(attempt, finalConfig);

      if (process.env.NODE_ENV === 'development') {
        console.log(
          `[API] Retrying (${attempt + 1}/${finalConfig.maxRetries}) after ${Math.round(delay)}ms. Reason: ${lastError.message}`
        );
      }

      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError ?? new ApiException('Max retries reached');
}

// ── useAbortController hook (Task 56) ──────────────────────────

/**
 * Creates an AbortController and returns helpers for request cancellation.
 * For use in non-React contexts. See hooks/useAbortController.ts for React hook.
 */
export function createAbortController(): {
  signal: AbortSignal;
  abort: () => void;
  isAborted: () => boolean;
} {
  const controller = new AbortController();
  return {
    signal: controller.signal,
    abort: () => controller.abort(),
    isAborted: () => controller.signal.aborted,
  };
}

// ── Offline Detection (Task 57) ────────────────────────────────

export function isOffline(): boolean {
  if (typeof navigator === 'undefined') return false;
  return !navigator.onLine;
}
