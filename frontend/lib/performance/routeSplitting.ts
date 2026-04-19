/**
 * Route-based Code Splitting Configuration
 *
 * Defines bundle size targets per route type.
 * Next.js App Router automatically splits by route segment.
 */

export const ROUTE_BUNDLE_TARGETS = {
  /** Homepage — keep minimal for fast LCP */
  homepage: {
    route: '/',
    targetKB: 150,
    criticalModules: ['hero', 'product-grid', 'header'],
  },

  /** Product listing — filters add weight */
  productListing: {
    route: '/products',
    targetKB: 180,
    criticalModules: ['filters', 'product-grid', 'pagination'],
  },

  /** Product detail — gallery + reviews */
  productDetail: {
    route: '/products/[slug]',
    targetKB: 200,
    criticalModules: ['gallery', 'product-info', 'add-to-cart'],
    lazyModules: ['reviews', 'related-products'],
  },

  /** Cart page */
  cart: {
    route: '/cart',
    targetKB: 120,
    criticalModules: ['cart-items', 'summary'],
  },

  /** Checkout — forms are heavy */
  checkout: {
    route: '/checkout',
    targetKB: 250,
    criticalModules: ['forms', 'steps', 'payment'],
  },

  /** Dashboard — admin features */
  dashboard: {
    route: '/dashboard',
    targetKB: 250,
    criticalModules: ['layout', 'stats'],
    lazyModules: ['charts', 'reports'],
  },
} as const;
