/**
 * Build-time Data Cache
 *
 * LRU cache for build-time data fetching.
 * Prevents redundant API calls during static generation.
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

class BuildTimeCache {
  private cache = new Map<string, CacheEntry<unknown>>();
  private maxEntries: number;

  constructor(maxEntries: number = 100) {
    this.maxEntries = maxEntries;
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key) as CacheEntry<T> | undefined;
    if (!entry) return null;

    // Check TTL
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  set<T>(key: string, data: T, ttlMs: number = 5 * 60 * 1000): void {
    // Evict oldest if at capacity
    if (this.cache.size >= this.maxEntries) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey !== undefined) {
        this.cache.delete(oldestKey);
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttlMs,
    });
  }

  /** Fetch with cache — deduplicate build-time requests */
  async getOrFetch<T>(
    key: string,
    fetchFn: () => Promise<T>,
    ttlMs: number = 5 * 60 * 1000
  ): Promise<T> {
    const cached = this.get<T>(key);
    if (cached !== null) return cached;

    const data = await fetchFn();
    this.set(key, data, ttlMs);
    return data;
  }

  clear(): void {
    this.cache.clear();
  }

  get size(): number {
    return this.cache.size;
  }

  get hitRate(): string {
    return `${this.cache.size} entries cached`;
  }
}

/** Singleton build-time cache instance */
export const buildCache = new BuildTimeCache(100);

// ── Pre-configured cache fetchers ───────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/** Cached categories fetch — reuse across pages */
export async function getCachedCategories() {
  return buildCache.getOrFetch('categories', async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/store/categories/`);
      if (!res.ok) return [];
      const data = await res.json();
      return data.results ?? data ?? [];
    } catch {
      return [];
    }
  }, 10 * 60 * 1000); // 10 min TTL
}

/** Cached site config fetch — reuse across all pages */
export async function getCachedSiteConfig() {
  return buildCache.getOrFetch('site-config', async () => {
    return {
      siteName: process.env.NEXT_PUBLIC_SITE_NAME || 'LankaCommerce Cloud',
      currency: process.env.NEXT_PUBLIC_DEFAULT_CURRENCY || 'LKR',
      locale: process.env.NEXT_PUBLIC_DEFAULT_LOCALE || 'en-LK',
      timezone: process.env.NEXT_PUBLIC_DEFAULT_TIMEZONE || 'Asia/Colombo',
    };
  }, 60 * 60 * 1000); // 1 hour TTL
}
