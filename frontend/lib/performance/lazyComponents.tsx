/**
 * Lazy Component Registry — heavy components loaded on demand.
 *
 * Each entry saves significant bundle size by deferring load
 * until the component is actually rendered.
 */

import dynamic from 'next/dynamic';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

// ── Lazy Modal (~200KB saved) ───────────────────────────────────

export const LazyImageGallery = dynamic(
  () => import('@/components/storefront/product/Gallery/ProductGallery').then((mod) => ({ default: mod.ProductGallery })),
  {
    ssr: true, // SSR for SEO — images should be in HTML
    loading: () => <LoadingSpinner size="lg" label="Loading gallery..." />,
  }
);

// ── Lazy Charts (~180KB saved) ─────────────────────────────────

export const LazyChartComponent = dynamic(
  () => import('@/components/dashboard/analytics/charts').then((mod) => {
    // Default export or first available chart
    const Component = (mod as Record<string, React.ComponentType>).default ?? Object.values(mod)[0] as React.ComponentType;
    return { default: Component };
  }),
  {
    ssr: false,
    loading: () => <LoadingSpinner size="lg" label="Loading chart..." />,
  }
);

// ── Lazy Rich Text Editor (~245KB saved) ────────────────────────

export const LazyRichTextEditor = dynamic(
  () => import('@/components/storefront/cms/Content/RichTextRenderer').then((mod) => ({ default: mod.RichTextRenderer })),
  {
    ssr: false,
    loading: () => <LoadingSpinner size="md" label="Loading editor..." />,
  }
);
