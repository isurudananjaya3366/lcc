// ─── Token Service ──────────────────────────────────────────────────────────
// Cookie-based token storage for storefront auth.
// Uses regular cookies with Secure + SameSite=Strict.
// In production, the backend would set httpOnly cookies directly.
// ────────────────────────────────────────────────────────────────────────────

const ACCESS_TOKEN_KEY = 'lcc_access_token';
const REFRESH_TOKEN_KEY = 'lcc_refresh_token';
const REMEMBER_ME_KEY = 'lcc_remember_me';

// ─── Cookie Helpers ─────────────────────────────────────────────────────────

function isBrowser(): boolean {
  return typeof window !== 'undefined' && typeof document !== 'undefined';
}

function setCookie(name: string, value: string, maxAgeSeconds: number): void {
  if (!isBrowser()) return;
  const secure = window.location.protocol === 'https:' ? '; Secure' : '';
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; SameSite=Strict${secure}`;
}

function getCookie(name: string): string | null {
  if (!isBrowser()) return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match?.[1] != null ? decodeURIComponent(match[1]) : null;
}

function deleteCookie(name: string): void {
  if (!isBrowser()) return;
  document.cookie = `${name}=; path=/; max-age=0; SameSite=Strict`;
}

// ─── Expiry Constants (seconds) ─────────────────────────────────────────────

const ACCESS_DEFAULT_MAX_AGE = 15 * 60; // 15 minutes
const REFRESH_DEFAULT_MAX_AGE = 7 * 24 * 60 * 60; // 7 days
const REFRESH_REMEMBER_MAX_AGE = 30 * 24 * 60 * 60; // 30 days

// ─── Public API ─────────────────────────────────────────────────────────────

export function getAccessToken(): string | null {
  return getCookie(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token: string, rememberMe?: boolean): void {
  const maxAge = rememberMe ? REFRESH_DEFAULT_MAX_AGE : ACCESS_DEFAULT_MAX_AGE;
  setCookie(ACCESS_TOKEN_KEY, token, maxAge);
}

export function getRefreshToken(): string | null {
  return getCookie(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(token: string, rememberMe?: boolean): void {
  const maxAge = rememberMe ? REFRESH_REMEMBER_MAX_AGE : REFRESH_DEFAULT_MAX_AGE;
  setCookie(REFRESH_TOKEN_KEY, token, maxAge);
}

export function clearTokens(): void {
  deleteCookie(ACCESS_TOKEN_KEY);
  deleteCookie(REFRESH_TOKEN_KEY);
  deleteCookie(REMEMBER_ME_KEY);
}

export function getRememberMe(): boolean {
  return getCookie(REMEMBER_ME_KEY) === '1';
}

export function setRememberMe(value: boolean): void {
  if (value) {
    setCookie(REMEMBER_ME_KEY, '1', REFRESH_REMEMBER_MAX_AGE);
  } else {
    deleteCookie(REMEMBER_ME_KEY);
  }
}

export function isTokenExpired(token: string | null, bufferSeconds: number = 60): boolean {
  if (!token) return true;

  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) return true;

    const payload = JSON.parse(atob(parts[1]));
    if (!payload.exp) return true;

    const expiresAt = (payload.exp as number) * 1000;
    const now = Date.now();
    const bufferMs = bufferSeconds * 1000;

    return now >= expiresAt - bufferMs;
  } catch {
    return true;
  }
}

export function getTokenExpiryMs(token: string | null): number | null {
  if (!token) return null;

  try {
    const parts = token.split('.');
    if (parts.length !== 3 || !parts[1]) return null;

    const payload = JSON.parse(atob(parts[1]));
    if (!payload.exp) return null;

    return (payload.exp as number) * 1000 - Date.now();
  } catch {
    return null;
  }
}
