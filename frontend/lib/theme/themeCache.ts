// ================================================================
// Theme Cache (localStorage)
// ================================================================
// Manages theme caching in localStorage with expiration.
// ================================================================

import type { Theme, ThemeCacheEntry } from '@/types/storefront/theme.types';

const CACHE_KEY_PREFIX = 'lcc-theme-';
const CACHE_MAX_AGE_MS = 60 * 60 * 1000; // 1 hour
const CACHE_VERSION = '1';

// ─── Helpers ────────────────────────────────────────────────────

function getCacheKey(tenantId: string): string {
  return `${CACHE_KEY_PREFIX}${tenantId || 'default'}`;
}

function isClient(): boolean {
  return typeof window !== 'undefined';
}

// ─── Public API ─────────────────────────────────────────────────

export function getCachedTheme(tenantId: string): Theme | null {
  if (!isClient()) return null;

  try {
    const raw = localStorage.getItem(getCacheKey(tenantId));
    if (!raw) return null;

    const entry: ThemeCacheEntry = JSON.parse(raw);

    if (entry.version !== CACHE_VERSION) {
      removeCachedTheme(tenantId);
      return null;
    }

    const age = Date.now() - entry.timestamp;
    if (age > CACHE_MAX_AGE_MS) {
      return null; // stale but keep for fallback
    }

    return entry.theme;
  } catch {
    removeCachedTheme(tenantId);
    return null;
  }
}

export function getStaleCachedTheme(tenantId: string): Theme | null {
  if (!isClient()) return null;

  try {
    const raw = localStorage.getItem(getCacheKey(tenantId));
    if (!raw) return null;

    const entry: ThemeCacheEntry = JSON.parse(raw);
    return entry.theme;
  } catch {
    return null;
  }
}

export function setCachedTheme(tenantId: string, theme: Theme): void {
  if (!isClient()) return;

  try {
    const entry: ThemeCacheEntry = {
      theme,
      timestamp: Date.now(),
      version: CACHE_VERSION,
      tenantId,
    };
    localStorage.setItem(getCacheKey(tenantId), JSON.stringify(entry));
  } catch {
    // Storage full or unavailable — fail silently
  }
}

export function removeCachedTheme(tenantId: string): void {
  if (!isClient()) return;

  try {
    localStorage.removeItem(getCacheKey(tenantId));
  } catch {
    // Fail silently
  }
}

export function isCacheFresh(tenantId: string): boolean {
  if (!isClient()) return false;

  try {
    const raw = localStorage.getItem(getCacheKey(tenantId));
    if (!raw) return false;

    const entry: ThemeCacheEntry = JSON.parse(raw);
    return Date.now() - entry.timestamp < CACHE_MAX_AGE_MS;
  } catch {
    return false;
  }
}
