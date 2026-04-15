import { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface JwtPayload {
  user_id: number;
  email: string;
  exp: number;
  iat: number;
  token_type: string;
}

export interface TokenStorage {
  accessToken: string | null;
  refreshToken: string | null;
  expiresAt: number | null;
  tokenType: string;
}

// ─── Token Storage Keys ────────────────────────────────────────────────────

const ACCESS_TOKEN_KEY = 'store-auth-token';
const REFRESH_TOKEN_KEY = 'store-refresh-token';
const GUEST_ID_KEY = 'store-guest-id';

// ─── Token Helpers ──────────────────────────────────────────────────────────

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function setRefreshToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function getGuestId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(GUEST_ID_KEY);
}

// ─── JWT Utilities ──────────────────────────────────────────────────────────

export function decodeJwt(token: string): JwtPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) return null;
    const payload = JSON.parse(atob(parts[1]));
    return payload as JwtPayload;
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string): boolean {
  const payload = decodeJwt(token);
  if (!payload) return true;
  // 5-minute buffer before actual expiry
  const bufferMs = 5 * 60 * 1000;
  return Date.now() >= payload.exp * 1000 - bufferMs;
}

export function isTokenValid(token: string): boolean {
  if (!token) return false;
  const parts = token.split('.');
  if (parts.length !== 3) return false;
  return !isTokenExpired(token);
}

// ─── Token Refresh ──────────────────────────────────────────────────────────

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onTokenRefreshed(token: string): void {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback: (token: string) => void): void {
  refreshSubscribers.push(callback);
}

async function refreshAccessToken(client: AxiosInstance): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    // Use a clean axios instance to avoid interceptor loops
    const { default: axios } = await import('axios');
    const baseURL = client.defaults.baseURL?.replace('/api/v1/store', '') || '';
    const response = await axios.post(`${baseURL}/api/v1/auth/token/refresh/`, {
      refresh: refreshToken,
    });

    const newToken = response.data.access;
    if (newToken) {
      setAccessToken(newToken);
      if (response.data.refresh) {
        setRefreshToken(response.data.refresh);
      }
      return newToken;
    }
    return null;
  } catch {
    clearTokens();
    return null;
  }
}

// ─── Interceptor Setup ─────────────────────────────────────────────────────

export function setupAuthInterceptor(instance: AxiosInstance): void {
  instance.interceptors.request.use(
    async (config: InternalAxiosRequestConfig) => {
      const token = getAccessToken();

      if (token && isTokenValid(token)) {
        config.headers.Authorization = `Bearer ${token}`;
        return config;
      }

      // Token exists but expired — attempt refresh
      if (token && isTokenExpired(token)) {
        if (!isRefreshing) {
          isRefreshing = true;
          const newToken = await refreshAccessToken(instance);
          isRefreshing = false;

          if (newToken) {
            onTokenRefreshed(newToken);
            config.headers.Authorization = `Bearer ${newToken}`;
            return config;
          }
          // Refresh failed — proceed without auth
          return config;
        }

        // Another refresh is in progress, queue this request
        return new Promise((resolve) => {
          addRefreshSubscriber((newToken: string) => {
            config.headers.Authorization = `Bearer ${newToken}`;
            resolve(config);
          });
        });
      }

      // No token — check guest mode
      const guestId = getGuestId();
      if (guestId) {
        config.headers['X-Guest-Session'] = guestId;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );
}
