/**
 * Type-safe LocalStorage Cache with TTL
 *
 * SECURITY: Never store auth tokens, passwords, or sensitive data.
 * Only for non-sensitive preferences and UI state.
 */

interface CachedItem<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

const MAX_ENTRIES = 50;
const CACHE_PREFIX = 'lcc_cache_';

/** Get item from localStorage with TTL check */
export function getCached<T>(key: string): T | null {
  if (typeof window === 'undefined') return null;

  try {
    const raw = localStorage.getItem(`${CACHE_PREFIX}${key}`);
    if (!raw) return null;

    const item: CachedItem<T> = JSON.parse(raw);

    // Check expiration
    if (Date.now() - item.timestamp > item.ttl) {
      localStorage.removeItem(`${CACHE_PREFIX}${key}`);
      return null;
    }

    return item.data;
  } catch {
    return null;
  }
}

/** Set item in localStorage with TTL */
export function setCached<T>(key: string, data: T, ttlMs: number = 30 * 60 * 1000): void {
  if (typeof window === 'undefined') return;

  try {
    // Enforce entry limit (LRU eviction)
    enforceLimits();

    const item: CachedItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttlMs,
    };

    localStorage.setItem(`${CACHE_PREFIX}${key}`, JSON.stringify(item));
  } catch (e) {
    // Storage full — evict oldest entries
    if (e instanceof DOMException && e.name === 'QuotaExceededError') {
      evictOldest(5);
      try {
        const item: CachedItem<T> = { data, timestamp: Date.now(), ttl: ttlMs };
        localStorage.setItem(`${CACHE_PREFIX}${key}`, JSON.stringify(item));
      } catch {
        // Give up if still full
      }
    }
  }
}

/** Remove cached item */
export function removeCached(key: string): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(`${CACHE_PREFIX}${key}`);
}

/** Clear all LCC cache entries */
export function clearCache(): void {
  if (typeof window === 'undefined') return;

  const keys = Object.keys(localStorage).filter((k) => k.startsWith(CACHE_PREFIX));
  keys.forEach((k) => localStorage.removeItem(k));
}

// ── Internal helpers ────────────────────────────────────────────

function enforceLimits(): void {
  const keys = Object.keys(localStorage).filter((k) => k.startsWith(CACHE_PREFIX));
  if (keys.length >= MAX_ENTRIES) {
    evictOldest(keys.length - MAX_ENTRIES + 1);
  }
}

function evictOldest(count: number): void {
  const keys = Object.keys(localStorage).filter((k) => k.startsWith(CACHE_PREFIX));

  const entries = keys.map((key) => {
    try {
      const item = JSON.parse(localStorage.getItem(key) || '{}');
      return { key, timestamp: item.timestamp || 0 };
    } catch {
      return { key, timestamp: 0 };
    }
  });

  entries.sort((a, b) => a.timestamp - b.timestamp);
  entries.slice(0, count).forEach(({ key }) => localStorage.removeItem(key));
}

// ── Pre-configured cache keys (what we store) ───────────────────

export const CACHE_KEYS = {
  /** Theme preference (light/dark) */
  theme: 'theme',
  /** Recently viewed product slugs */
  recentlyViewed: 'recently-viewed',
  /** Recent search terms */
  recentSearches: 'recent-searches',
  /** Cart backup (for recovery) */
  cartBackup: 'cart-backup',
  /** User preferences (locale, currency) */
  preferences: 'preferences',
} as const;
