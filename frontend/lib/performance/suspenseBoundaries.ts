/**
 * Suspense Boundary Configuration
 *
 * Defines where React Suspense boundaries should wrap for
 * streaming SSR and progressive loading.
 */

export const SUSPENSE_CONFIG = {
  /** Components that should be wrapped in Suspense */
  boundaries: {
    productGrid: { fallback: 'GridSkeleton', timeout: 3000 },
    productDetail: { fallback: 'ProductDetailSkeleton', timeout: 3000 },
    searchResults: { fallback: 'GridSkeleton', timeout: 2000 },
    cart: { fallback: 'CartSkeleton', timeout: 2000 },
    checkout: { fallback: 'LoadingSpinner', timeout: 5000 },
    reviews: { fallback: 'ContentSkeleton', timeout: 3000 },
    relatedProducts: { fallback: 'GridSkeleton', timeout: 3000 },
    blogPosts: { fallback: 'ContentSkeleton', timeout: 3000 },
  },

  /** Streaming SSR: components loaded in priority order */
  streamingOrder: [
    'header',
    'hero',
    'primaryContent',
    'sidebar',
    'relatedContent',
    'footer',
  ],
} as const;
