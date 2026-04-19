/**
 * Prefetch & Preload Utilities
 *
 * Manages resource hints (preload, prefetch, preconnect)
 * and hover-based route prefetching.
 */

// ── Resource Hints ──────────────────────────────────────────────

export type ResourcePriority = 'preload' | 'prefetch' | 'preconnect' | 'dns-prefetch';

export interface ResourceHint {
  rel: ResourcePriority;
  href: string;
  as?: string;
  type?: string;
  crossOrigin?: 'anonymous' | 'use-credentials';
}

/** Critical resource hints for <head> */
export const RESOURCE_HINTS: ResourceHint[] = [
  // Preconnect to API server
  { rel: 'preconnect', href: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' },
  // Preconnect to CDN
  { rel: 'preconnect', href: process.env.NEXT_PUBLIC_CDN_URL || '', crossOrigin: 'anonymous' },
  // DNS prefetch for analytics
  { rel: 'dns-prefetch', href: 'https://www.google-analytics.com' },
].filter((h) => h.href);

// ── Link Prefetch Config ────────────────────────────────────────

export const PREFETCH_CONFIG = {
  /** Enable prefetch on next/link (default: true in viewport) */
  enabled: true,

  /** Maximum number of concurrent prefetches */
  maxConcurrent: 6,

  /** Connection-aware: disable on slow connections */
  respectConnectionSpeed: true,

  /** Prefetch first N product links on listing pages */
  productPrefetchLimit: 6,
} as const;

// ── Hover Prefetch ──────────────────────────────────────────────

let prefetchTimer: ReturnType<typeof setTimeout> | null = null;

/**
 * Debounced hover prefetch — call router.prefetch() after 150ms hover.
 * Cancels if mouse leaves before delay.
 */
export function onHoverPrefetch(
  href: string,
  prefetchFn: (href: string) => void,
  delay: number = 150
): { onMouseEnter: () => void; onMouseLeave: () => void } {
  return {
    onMouseEnter: () => {
      // Skip on touch devices or slow connections
      if (isTouchDevice() || isSlowConnection()) return;

      prefetchTimer = setTimeout(() => {
        prefetchFn(href);
      }, delay);
    },
    onMouseLeave: () => {
      if (prefetchTimer) {
        clearTimeout(prefetchTimer);
        prefetchTimer = null;
      }
    },
  };
}

function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false;
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

function isSlowConnection(): boolean {
  if (typeof navigator === 'undefined') return false;
  const conn = (navigator as Navigator & { connection?: { effectiveType?: string } }).connection;
  return conn?.effectiveType === '2g' || conn?.effectiveType === 'slow-2g';
}
