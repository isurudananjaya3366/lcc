/**
 * Performance Configuration — Bundle size limits and targets.
 */

export const PERFORMANCE_BUDGETS = {
  /** Route-specific bundle limits (gzipped KB) */
  routes: {
    homepage: 150,
    productListing: 180,
    productDetail: 200,
    cart: 120,
    checkout: 250,
    dashboard: 250,
    blog: 150,
  },

  /** Overall limits */
  mainBundle: 100,      // Main JS bundle (gzipped)
  firstLoad: 200,       // First load JS (gzipped)
  vendorChunk: 150,     // Vendor chunk (gzipped)
  cssTotal: 50,         // Total CSS (gzipped)

  /** Core Web Vitals targets */
  webVitals: {
    LCP: 2500,          // ms — Largest Contentful Paint
    FID: 100,           // ms — First Input Delay
    CLS: 0.1,           // score — Cumulative Layout Shift
    FCP: 1500,          // ms — First Contentful Paint
    TTFB: 600,          // ms — Time to First Byte
    INP: 200,           // ms — Interaction to Next Paint
  },

  /** Lighthouse score targets */
  lighthouse: {
    performance: 90,
    accessibility: 95,
    bestPractices: 90,
    seo: 90,
  },
} as const;

export type PerformanceBudgets = typeof PERFORMANCE_BUDGETS;
