/**
 * Cache Busting Utilities
 *
 * Next.js automatically hashes filenames for JS/CSS bundles.
 * This module handles additional cache busting needs.
 */

/** Current build version — injected at build time */
export const BUILD_VERSION = process.env.NEXT_PUBLIC_BUILD_VERSION || 'dev';

/** Generate version-aware URL for non-hashed assets */
export function versionedUrl(path: string): string {
  const separator = path.includes('?') ? '&' : '?';
  return `${path}${separator}v=${BUILD_VERSION}`;
}

/** Version manifest for service worker cache invalidation */
export const VERSION_MANIFEST = {
  version: BUILD_VERSION,
  timestamp: process.env.NEXT_PUBLIC_BUILD_TIME || new Date().toISOString(),
  caches: {
    'static-assets': 'v1',
    'fonts': 'v1',
    'images': 'v1',
    'api-responses': 'v1',
  },
} as const;
