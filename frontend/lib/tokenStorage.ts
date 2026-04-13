/**
 * Token Storage Module
 *
 * Manages JWT access and refresh token persistence using localStorage.
 * Provides functions to get, set, clear, and validate token expiration.
 *
 * Security note: In production, consider HTTP-only cookies for enhanced
 * XSS protection. This localStorage approach is suitable for development
 * and can be swapped transparently via these functions.
 */

const ACCESS_TOKEN_KEY = 'lcc_access_token';
const REFRESH_TOKEN_KEY = 'lcc_refresh_token';

/**
 * Check if localStorage is available (SSR safety).
 */
function isStorageAvailable(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    const test = '__storage_test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch {
    return false;
  }
}

/**
 * Retrieve the stored access token.
 * @returns The access token string, or null if not found or unavailable.
 */
export function getAccessToken(): string | null {
  if (!isStorageAvailable()) return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Store the access token.
 * @param token - JWT access token string.
 */
export function setAccessToken(token: string): void {
  if (!isStorageAvailable()) return;
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

/**
 * Retrieve the stored refresh token.
 * @returns The refresh token string, or null if not found or unavailable.
 */
export function getRefreshToken(): string | null {
  if (!isStorageAvailable()) return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store the refresh token.
 * @param token - JWT refresh token string.
 */
export function setRefreshToken(token: string): void {
  if (!isStorageAvailable()) return;
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

/**
 * Clear both access and refresh tokens.
 * Called on logout or when tokens become permanently invalid.
 */
export function clearTokens(): void {
  if (!isStorageAvailable()) return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Check if a JWT token is expired.
 *
 * Decodes the JWT payload to read the `exp` claim and compares
 * it against the current time with an optional buffer (default 60s)
 * to allow proactive refresh before actual expiration.
 *
 * @param token - JWT token string, or null.
 * @param bufferSeconds - Seconds before actual expiry to consider expired (default: 60).
 * @returns true if the token is null, malformed, or expired; false otherwise.
 */
export function isTokenExpired(
  token: string | null,
  bufferSeconds: number = 60
): boolean {
  if (!token) return true;

  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;

    const payload = JSON.parse(atob(parts[1]));
    if (!payload.exp) return true;

    const expiresAt = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();
    const bufferMs = bufferSeconds * 1000;

    return now >= expiresAt - bufferMs;
  } catch {
    return true;
  }
}
