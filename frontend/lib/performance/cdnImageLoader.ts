/**
 * Custom Next.js image loader for CDN delivery.
 * Used as the `loader` prop on next/image when CDN is configured.
 */

import type { ImageLoaderProps } from 'next/image';

const CDN_BASE_URL = process.env.NEXT_PUBLIC_CDN_URL || '';

export function cdnImageLoader({ src, width, quality }: ImageLoaderProps): string {
  if (!CDN_BASE_URL) {
    // Fallback to default Next.js optimization
    return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality || 75}`;
  }

  const params = new URLSearchParams({
    w: String(width),
    q: String(quality || 75),
    f: 'auto', // auto-format (WebP/AVIF)
  });

  // Absolute URLs pass through
  if (src.startsWith('http')) {
    return `${CDN_BASE_URL}/cdn-cgi/image/${params.toString()}/${src}`;
  }

  return `${CDN_BASE_URL}${src}?${params.toString()}`;
}

export const CDN_CACHE_CONFIG = {
  browserTTL: 7 * 24 * 60 * 60,    // 7 days
  cdnTTL: 30 * 24 * 60 * 60,       // 30 days
  immutableAssets: 365 * 24 * 60 * 60, // 1 year
} as const;
