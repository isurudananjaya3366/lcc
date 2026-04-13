/**
 * Request Interceptors
 *
 * Intercepts outgoing Axios requests to attach:
 * - Authorization Bearer token (JWT)
 * - X-Tenant-ID header for multi-tenant routing
 * - X-Request-ID header for distributed tracing
 * - Request timestamp metadata for performance logging
 */

import type { InternalAxiosRequestConfig } from 'axios';
import { getAccessToken } from '@/lib/tokenStorage';

// ── Custom Metadata Type ───────────────────────────────────────

declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: {
      requestId?: string;
      requestTimestamp?: number;
      startPerformance?: number;
    };
    _retry?: boolean;
    skipAuth?: boolean;
    skipTenant?: boolean;
  }
}

// ── Public Endpoints (no auth required) ────────────────────────

const PUBLIC_ENDPOINTS = [
  '/auth/login',
  '/auth/register',
  '/auth/forgot-password',
  '/auth/reset-password',
  '/health',
];

function isPublicEndpoint(url?: string): boolean {
  if (!url) return false;
  return PUBLIC_ENDPOINTS.some((endpoint) => url.includes(endpoint));
}

// ── Request Interceptor ────────────────────────────────────────

export function requestInterceptor(
  config: InternalAxiosRequestConfig
): InternalAxiosRequestConfig {
  // Ensure headers object exists
  config.headers = config.headers || {};

  // 1. Authorization header (Task 32)
  if (!config.skipAuth && !isPublicEndpoint(config.url)) {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }

  // 2. Tenant header (Task 33)
  if (!config.skipTenant) {
    const tenantId = getTenantId();
    if (tenantId) {
      config.headers['X-Tenant-ID'] = tenantId;
    }
  }

  // 3. Request ID header (Task 34)
  if (!config.headers['X-Request-ID']) {
    config.headers['X-Request-ID'] = generateRequestId();
  }

  // 4. Request timestamp metadata (Task 35)
  config.metadata = {
    ...config.metadata,
    requestId: config.headers['X-Request-ID'] as string,
    requestTimestamp: Date.now(),
    startPerformance:
      typeof performance !== 'undefined' ? performance.now() : Date.now(),
  };

  // Dev logging
  if (process.env.NODE_ENV === 'development') {
    console.log(
      `[API] → ${config.method?.toUpperCase()} ${config.url}`,
      `[${config.headers['X-Request-ID']}]`
    );
  }

  return config;
}

export function requestErrorHandler(error: unknown): Promise<never> {
  return Promise.reject(error);
}

// ── Helpers ────────────────────────────────────────────────────

function generateRequestId(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for environments without crypto.randomUUID
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
}

function getTenantId(): string | null {
  if (typeof window === 'undefined') return null;
  const hostname = window.location.hostname;
  // Extract subdomain as tenant identifier
  const parts = hostname.split('.');
  if (parts.length > 2) {
    return parts[0];
  }
  return null;
}
