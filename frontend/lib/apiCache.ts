/**
 * API Cache Layer
 *
 * In-memory cache for GET requests with TTL, size limits,
 * LRU eviction, and pattern-based invalidation.
 */

// ── Types ──────────────────────────────────────────────────────

export interface CacheOptions {
  maxAge?: number;
  maxSize?: number;
  enabled?: boolean;
  exclude?: RegExp[];
}

export interface CacheEntry<T = unknown> {
  key: string;
  data: T;
  timestamp: number;
  expiresAt: number;
  accessCount: number;
  lastAccessed: number;
}

export interface CacheStats {
  hits: number;
  misses: number;
  hitRate: number;
  size: number;
  oldestEntry: number | null;
  newestEntry: number | null;
}

const DEFAULT_OPTIONS: Required<CacheOptions> = {
  maxAge: 300_000, // 5 minutes
  maxSize: 100,
  enabled: true,
  exclude: [],
};

// ── Cache Implementation ───────────────────────────────────────

export class ApiCache {
  private cache = new Map<string, CacheEntry>();
  private options: Required<CacheOptions>;
  private hits = 0;
  private misses = 0;
  private accessCounter = 0;

  constructor(options?: CacheOptions) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
  }

  // ── Key Generation ───────────────────────────────────────────

  static generateKey(method: string, url: string, params?: Record<string, unknown>): string {
    let key = `${method.toUpperCase()}:${url}`;
    if (params && Object.keys(params).length > 0) {
      const sorted = Object.keys(params)
        .sort()
        .map((k) => `${k}=${String(params[k])}`)
        .join('&');
      key += `?${sorted}`;
    }
    return key;
  }

  // ── Get / Set ────────────────────────────────────────────────

  get<T>(key: string): T | null {
    if (!this.options.enabled) return null;

    const entry = this.cache.get(key);
    if (!entry) {
      this.misses++;
      return null;
    }

    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      this.misses++;
      return null;
    }

    entry.accessCount++;
    entry.lastAccessed = ++this.accessCounter;
    this.hits++;
    return entry.data as T;
  }

  set<T>(key: string, data: T, maxAge?: number): void {
    if (!this.options.enabled) return;

    // Check exclusion patterns
    for (const pattern of this.options.exclude) {
      if (pattern.test(key)) return;
    }

    // Evict if at capacity
    if (this.cache.size >= this.options.maxSize && !this.cache.has(key)) {
      this.evictLRU();
    }

    const now = Date.now();
    this.cache.set(key, {
      key,
      data,
      timestamp: now,
      expiresAt: now + (maxAge ?? this.options.maxAge),
      accessCount: 0,
      lastAccessed: ++this.accessCounter,
    });
  }

  // ── Invalidation ────────────────────────────────────────────

  invalidate(key: string): boolean {
    return this.cache.delete(key);
  }

  invalidatePattern(pattern: string | RegExp): number {
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;
    let count = 0;
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
        count++;
      }
    }
    return count;
  }

  invalidateAll(): void {
    this.cache.clear();
    this.hits = 0;
    this.misses = 0;
  }

  /**
   * Auto-invalidate related cache entries on mutating requests.
   * Call after POST/PUT/PATCH/DELETE to clear stale data.
   */
  autoInvalidate(method: string, url: string): void {
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
      // Remove exact match and list endpoint
      const base = url.replace(/\/[^/]+\/?$/, '');
      this.invalidatePattern(new RegExp(`^GET:${this.escapeRegex(url)}`));
      this.invalidatePattern(new RegExp(`^GET:${this.escapeRegex(base)}`));
    }
  }

  // ── Eviction (LRU) ──────────────────────────────────────────

  private evictLRU(): void {
    let lruKey: string | null = null;
    let lruTime = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.lastAccessed < lruTime) {
        lruTime = entry.lastAccessed;
        lruKey = key;
      }
    }

    if (lruKey) this.cache.delete(lruKey);
  }

  // ── Maintenance ──────────────────────────────────────────────

  pruneExpired(): number {
    const now = Date.now();
    let count = 0;
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
        count++;
      }
    }
    return count;
  }

  // ── Stats ────────────────────────────────────────────────────

  getStats(): CacheStats {
    const total = this.hits + this.misses;
    let oldest: number | null = null;
    let newest: number | null = null;
    for (const entry of this.cache.values()) {
      if (oldest === null || entry.timestamp < oldest) oldest = entry.timestamp;
      if (newest === null || entry.timestamp > newest) newest = entry.timestamp;
    }
    return {
      hits: this.hits,
      misses: this.misses,
      hitRate: total > 0 ? this.hits / total : 0,
      size: this.cache.size,
      oldestEntry: oldest,
      newestEntry: newest,
    };
  }

  getKeys(): string[] {
    return Array.from(this.cache.keys());
  }

  getSize(): number {
    return this.cache.size;
  }

  private escapeRegex(s: string): string {
    return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

// ── Singleton ──────────────────────────────────────────────────

let globalCache: ApiCache | null = null;

export function getApiCache(options?: CacheOptions): ApiCache {
  if (!globalCache) {
    globalCache = new ApiCache(options);
  }
  return globalCache;
}

export function resetApiCache(): void {
  globalCache?.invalidateAll();
  globalCache = null;
}
