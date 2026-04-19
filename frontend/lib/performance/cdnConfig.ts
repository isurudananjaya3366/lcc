/**
 * CDN Configuration
 *
 * Edge caching rules, cache key optimization, and purge mechanisms.
 */

export const CDN_CONFIG = {
  /** CDN provider */
  provider: (process.env.NEXT_PUBLIC_CDN_PROVIDER || 'vercel') as 'vercel' | 'cloudflare',

  /** Edge caching rules */
  edgeRules: {
    /** Product API: 10 min edge cache */
    products: { sMaxAge: 600, staleWhileRevalidate: 86400 },
    /** Categories: 1 hour edge cache */
    categories: { sMaxAge: 3600, staleWhileRevalidate: 86400 },
    /** Static assets: 1 year */
    assets: { sMaxAge: 31536000, immutable: true },
    /** Images: 7 days */
    images: { sMaxAge: 604800, staleWhileRevalidate: 2592000 },
  },

  /** Cache key configuration */
  cacheKeys: {
    /** Include in cache key */
    include: ['pathname', 'search-params', 'accept-encoding'],
    /** Exclude from cache key (prevent cache fragmentation) */
    exclude: ['cookies', 'user-agent'],
  },

  /** Compression */
  compression: {
    brotli: true,
    gzip: true,
    minSize: 1024, // Only compress > 1KB
  },

  /** Purge configuration */
  purge: {
    /** API endpoint for manual purge */
    endpoint: process.env.CDN_PURGE_URL || '',
    /** Auth token for purge API */
    token: process.env.CDN_PURGE_TOKEN || '',
  },
} as const;

/** Purge CDN cache for specific paths */
export async function purgeCDNCache(paths: string[]): Promise<boolean> {
  if (!CDN_CONFIG.purge.endpoint || !CDN_CONFIG.purge.token) {
    console.warn('[CDN] Purge not configured');
    return false;
  }

  try {
    const res = await fetch(CDN_CONFIG.purge.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${CDN_CONFIG.purge.token}`,
      },
      body: JSON.stringify({ paths }),
    });
    return res.ok;
  } catch {
    console.error('[CDN] Purge failed');
    return false;
  }
}
