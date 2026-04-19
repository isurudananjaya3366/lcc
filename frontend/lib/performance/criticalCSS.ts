/**
 * Critical CSS Strategy
 *
 * Next.js handles critical CSS automatically:
 * - CSS Modules are scoped and loaded per-component
 * - Tailwind purges unused classes in production (~99% reduction)
 * - next/font injects font-face declarations inline
 *
 * This config ensures optimal CSS delivery strategy.
 */

export const CSS_STRATEGY = {
  /** Target critical CSS budget (inlined in <head>) */
  criticalBudget: 14 * 1024, // 14KB — fits in first TCP round-trip

  /** Tailwind purge config (handled by tailwind.config.ts) */
  purge: {
    enabled: true,
    layers: ['base', 'components', 'utilities'],
  },

  /** Route-based CSS splitting priorities */
  routePriority: {
    '/': ['layout', 'hero', 'product-grid'],
    '/products': ['layout', 'filters', 'product-grid'],
    '/products/[slug]': ['layout', 'gallery', 'product-info'],
    '/cart': ['layout', 'cart-items', 'summary'],
    '/checkout': ['layout', 'forms', 'steps'],
  },
} as const;
