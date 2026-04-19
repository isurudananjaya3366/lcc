/**
 * HTTP Cache Header Configuration
 *
 * Defines Cache-Control headers for different resource types.
 * Applied via Next.js middleware or API route handlers.
 */

export interface CacheHeaderConfig {
  'Cache-Control': string;
  ETag?: boolean;
  Vary?: string;
}

// ── Cache Policies ──────────────────────────────────────────────

export const CACHE_POLICIES: Record<string, CacheHeaderConfig> = {
  /** Product API responses — public, CDN-cacheable */
  products: {
    'Cache-Control': 'public, max-age=300, s-maxage=600, stale-while-revalidate=86400',
    ETag: true,
    Vary: 'Accept-Encoding',
  },

  /** Category API responses — longer cache */
  categories: {
    'Cache-Control': 'public, max-age=1800, s-maxage=3600, stale-while-revalidate=86400',
    ETag: true,
    Vary: 'Accept-Encoding',
  },

  /** Cart — private, no CDN caching */
  cart: {
    'Cache-Control': 'private, no-cache, no-store, must-revalidate',
  },

  /** User data — private */
  user: {
    'Cache-Control': 'private, max-age=0, must-revalidate',
  },

  /** Static assets — immutable long-cache */
  staticAssets: {
    'Cache-Control': 'public, max-age=31536000, immutable',
  },

  /** Images — long cache with revalidation */
  images: {
    'Cache-Control': 'public, max-age=604800, stale-while-revalidate=2592000',
    Vary: 'Accept',
  },

  /** Blog content — moderate cache */
  blog: {
    'Cache-Control': 'public, max-age=3600, s-maxage=7200, stale-while-revalidate=86400',
    ETag: true,
  },

  /** Search results — short cache */
  search: {
    'Cache-Control': 'public, max-age=60, s-maxage=300',
    Vary: 'Accept-Encoding',
  },
};

/** Generate ETag from content string */
export function generateETag(content: string): string {
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0; // Convert to 32-bit integer
  }
  return `"${Math.abs(hash).toString(36)}"`;
}

/** Apply cache headers to a Response */
export function applyCacheHeaders(
  headers: Headers,
  policy: keyof typeof CACHE_POLICIES
): void {
  const config = CACHE_POLICIES[policy];
  if (!config) return;

  headers.set('Cache-Control', config['Cache-Control']);
  if (config.Vary) headers.set('Vary', config.Vary);
}
