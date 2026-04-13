/**
 * Error Boundary Components
 *
 * Catches rendering errors in the component tree and displays
 * user-friendly fallback UI. Integrates with the API error handling
 * system (ApiException) and provides recovery mechanisms.
 */

'use client';

import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { ApiException } from '@/lib/apiError';
import { getErrorMessage } from '@/lib/apiError';

// ── Types ──────────────────────────────────────────────────────

interface ErrorBoundaryProps {
  children: ReactNode;
  /** Custom fallback UI to render when an error is caught */
  fallback?: ReactNode;
  /** Callback invoked when an error is caught */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  /** When any of these values change, the boundary resets */
  resetKeys?: unknown[];
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

// ── Error Logging Utility ──────────────────────────────────────

let lastLoggedAt = 0;
const LOG_RATE_LIMIT_MS = 5_000;

function logErrorToService(
  error: Error,
  errorInfo: ErrorInfo
): void {
  const now = Date.now();
  if (now - lastLoggedAt < LOG_RATE_LIMIT_MS) return;
  lastLoggedAt = now;

  const payload = {
    message: error.message,
    stack: error.stack,
    componentStack: errorInfo.componentStack,
    timestamp: new Date().toISOString(),
    userAgent:
      typeof navigator !== 'undefined' ? navigator.userAgent : 'SSR',
    url: typeof window !== 'undefined' ? window.location.href : '',
    ...(error instanceof ApiException && {
      apiCode: error.code,
      apiStatus: error.status,
      isNetworkError: error.isNetworkError,
      isTimeoutError: error.isTimeoutError,
    }),
  };

  // In production, send to external monitoring service (Sentry / LogRocket)
  if (process.env.NODE_ENV === 'production') {
    // Integration point: Sentry.captureException(error, { extra: payload });
    console.error('[ErrorBoundary] Error logged to monitoring', payload);
  } else {
    console.error('[ErrorBoundary] Caught error:', payload);
  }
}

// ── ErrorBoundary (General) ────────────────────────────────────

export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    logErrorToService(error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: ErrorBoundaryProps): void {
    if (!this.state.hasError) return;

    const prevKeys = prevProps.resetKeys ?? [];
    const nextKeys = this.props.resetKeys ?? [];

    const changed =
      prevKeys.length !== nextKeys.length ||
      prevKeys.some((k, i) => k !== nextKeys[i]);

    if (changed) {
      this.resetError();
    }
  }

  resetError = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const message = this.state.error
        ? getErrorMessage(this.state.error)
        : 'An unexpected error occurred.';

      return (
        <div
          role="alert"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
            minHeight: '200px',
            textAlign: 'center',
            gap: '1rem',
          }}
        >
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#e53e3e"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>

          <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#2d3748' }}>
            Something went wrong
          </h2>

          <p style={{ margin: 0, color: '#718096', maxWidth: '420px' }}>
            {message}
          </p>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              onClick={this.resetError}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#3182ce',
                color: '#fff',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
              }}
            >
              Try Again
            </button>

            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  window.location.href = '/';
                }
              }}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#e2e8f0',
                color: '#4a5568',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
              }}
            >
              Go to Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// ── ApiErrorBoundary (API-specific variant) ────────────────────

interface ApiErrorBoundaryProps extends ErrorBoundaryProps {
  /** Show retry suggestion for retryable errors */
  showRetryHint?: boolean;
}

export class ApiErrorBoundary extends Component<
  ApiErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ApiErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });
    logErrorToService(error, errorInfo);
    this.props.onError?.(error, errorInfo);
  }

  componentDidUpdate(prevProps: ApiErrorBoundaryProps): void {
    if (!this.state.hasError) return;

    const prevKeys = prevProps.resetKeys ?? [];
    const nextKeys = this.props.resetKeys ?? [];

    const changed =
      prevKeys.length !== nextKeys.length ||
      prevKeys.some((k, i) => k !== nextKeys[i]);

    if (changed) {
      this.resetError();
    }
  }

  resetError = (): void => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const err = this.state.error;
      const isApi = err instanceof ApiException;
      const message = err ? getErrorMessage(err) : 'An unexpected error occurred.';

      let hint = '';
      if (isApi && err.isNetworkError) {
        hint = 'Please check your internet connection and try again.';
      } else if (isApi && err.isTimeoutError) {
        hint = 'The request timed out. The server may be busy — try again shortly.';
      } else if (
        isApi &&
        this.props.showRetryHint !== false &&
        err.status &&
        err.status >= 500
      ) {
        hint = 'This may be a temporary issue. Retrying could help.';
      }

      return (
        <div
          role="alert"
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '2rem',
            minHeight: '200px',
            textAlign: 'center',
            gap: '1rem',
          }}
        >
          <svg
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#dd6b20"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>

          <h2 style={{ margin: 0, fontSize: '1.25rem', color: '#2d3748' }}>
            {isApi && err.isNetworkError
              ? 'Connection Problem'
              : isApi && err.isTimeoutError
                ? 'Request Timed Out'
                : 'Something went wrong'}
          </h2>

          <p style={{ margin: 0, color: '#718096', maxWidth: '420px' }}>
            {message}
          </p>

          {hint && (
            <p style={{ margin: 0, color: '#a0aec0', fontSize: '0.85rem', maxWidth: '420px' }}>
              {hint}
            </p>
          )}

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
            <button
              onClick={this.resetError}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#3182ce',
                color: '#fff',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
              }}
            >
              Try Again
            </button>

            <button
              onClick={() => {
                if (typeof window !== 'undefined') {
                  window.location.href = '/';
                }
              }}
              style={{
                padding: '0.5rem 1rem',
                backgroundColor: '#e2e8f0',
                color: '#4a5568',
                border: 'none',
                borderRadius: '0.375rem',
                cursor: 'pointer',
                fontSize: '0.875rem',
              }}
            >
              Go to Home
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
