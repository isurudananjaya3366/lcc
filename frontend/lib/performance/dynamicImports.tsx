/**
 * Dynamic Import Helpers — centralized lazy loading utilities.
 *
 * Usage:
 *   const LazyModal = createDynamicImport(() => import('@/components/Modal'), { ssr: false });
 */

import dynamic from 'next/dynamic';
import type { ComponentType } from 'react';

export interface DynamicImportOptions {
  ssr?: boolean;
  loading?: ComponentType;
}

/**
 * Create a dynamically imported component with sensible defaults.
 */
export function createDynamicImport<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  options: DynamicImportOptions = {}
): ComponentType<P> {
  const { ssr = false, loading } = options;

  return dynamic(importFn, {
    ssr,
    loading: loading ? () => {
      const LoadingComponent = loading;
      return <LoadingComponent />;
    } : undefined,
  });
}

// ── Pre-configured lazy components ──────────────────────────────

/** Lazy-loaded modal (Task 39) — ~200KB saved */
export const LazyModal = createDynamicImport(
  () => import('@/components/ui/dialog').then((mod) => ({ default: mod.Dialog })),
  { ssr: false }
);

/** Lazy-loaded rich text editor (Task 42) */
export const LazyRichText = createDynamicImport(
  () => import('@/components/storefront/cms/Content/RichTextRenderer').then((mod) => ({ default: mod.RichTextRenderer })),
  { ssr: false }
);
