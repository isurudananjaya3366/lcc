// ─── Store API Client ───────────────────────────────────────────────────────
// Fetch wrapper for storefront API calls with automatic token attachment
// and 401 retry via token refresh.
// ────────────────────────────────────────────────────────────────────────────

import { getAccessToken, getRefreshToken, setAccessToken, setRefreshToken, clearTokens, isTokenExpired, getRememberMe } from '@/services/storefront/tokenService';
import { refreshTokenApi } from '@/services/storefront/authService';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL
  ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1/store`
  : '/api/v1/store';

// Prevent concurrent refresh calls
let refreshPromise: Promise<boolean> | null = null;

async function attemptRefresh(): Promise<boolean> {
  if (refreshPromise) return refreshPromise;

  refreshPromise = (async () => {
    try {
      const refresh = getRefreshToken();
      if (!refresh || isTokenExpired(refresh, 0)) {
        clearTokens();
        return false;
      }

      const result = await refreshTokenApi();
      const responseAny = result as Record<string, unknown>;
      const rememberMe = getRememberMe();

      if (responseAny.access) {
        setAccessToken(responseAny.access as string, rememberMe);
      }
      if (responseAny.refresh) {
        setRefreshToken(responseAny.refresh as string, rememberMe);
      }

      return true;
    } catch {
      clearTokens();
      return false;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export interface StoreApiError {
  message: string;
  status: number;
  details?: Record<string, unknown>;
}

async function storeApiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;

  const makeRequest = async (token: string | null): Promise<Response> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    });
  };

  let token = getAccessToken();
  let response = await makeRequest(token);

  // On 401, try refreshing the token and retry once
  if (response.status === 401) {
    const refreshed = await attemptRefresh();
    if (refreshed) {
      token = getAccessToken();
      response = await makeRequest(token);
    } else {
      // Redirect to login
      if (typeof window !== 'undefined') {
        window.location.href = '/account/login';
      }
      throw {
        message: 'Session expired. Please log in again.',
        status: 401,
      } as StoreApiError;
    }
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw {
      message: body.detail || body.message || `Request failed (${response.status})`,
      status: response.status,
      details: body,
    } as StoreApiError;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

// ─── Convenience Methods ────────────────────────────────────────────────────

export const storeApi = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    storeApiFetch<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    storeApiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    storeApiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    }),

  patch: <T>(endpoint: string, data?: unknown, options?: RequestInit) =>
    storeApiFetch<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    storeApiFetch<T>(endpoint, { ...options, method: 'DELETE' }),
};
