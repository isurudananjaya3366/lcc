/**
 * Performance Test Configuration
 *
 * Defines test scenarios for homepage, product, category, and mobile.
 * Used by Lighthouse CI and manual testing.
 */

export interface PerformanceTestConfig {
  name: string;
  url: string;
  device: 'desktop' | 'mobile';
  runs: number;
  targets: {
    performance: number;
    lcp: number;    // ms
    fcp: number;    // ms
    cls: number;    // score
    fid: number;    // ms
    tti: number;    // ms
  };
  checks: string[];
}

// ── Test 90: Homepage Performance ───────────────────────────────

export const HOMEPAGE_TEST: PerformanceTestConfig = {
  name: 'Homepage Performance',
  url: '/',
  device: 'desktop',
  runs: 3,
  targets: {
    performance: 95,
    lcp: 2000,
    fcp: 1200,
    cls: 0.05,
    fid: 50,
    tti: 3000,
  },
  checks: [
    'Hero image uses priority loading',
    'Product grid images use lazy loading',
    'Fonts preloaded with display:swap',
    'Critical CSS inlined',
    'No render-blocking resources',
    'Images in WebP/AVIF format',
  ],
};

// ── Test 91: Product Page Performance ───────────────────────────

export const PRODUCT_PAGE_TEST: PerformanceTestConfig = {
  name: 'Product Page Performance',
  url: '/products/sample-product',
  device: 'desktop',
  runs: 3,
  targets: {
    performance: 90,
    lcp: 2200,
    fcp: 1500,
    cls: 0.08,
    fid: 80,
    tti: 3500,
  },
  checks: [
    'Main product image uses priority',
    'Gallery thumbnails use lazy loading',
    'Reviews loaded via Suspense',
    'Related products lazy loaded',
    'JSON-LD structured data present',
    'Image srcSet responsive',
  ],
};

// ── Test 92: Category Page Performance ──────────────────────────

export const CATEGORY_PAGE_TEST: PerformanceTestConfig = {
  name: 'Category Page Performance',
  url: '/products?category=spices',
  device: 'desktop',
  runs: 3,
  targets: {
    performance: 85,
    lcp: 2500,
    fcp: 1800,
    cls: 0.1,
    fid: 100,
    tti: 4000,
  },
  checks: [
    'Filter sidebar does not cause CLS',
    'Product grid uses consistent image sizes',
    'Pagination does not reload full page',
    'Filter interactions respond within 100ms',
  ],
};

// ── Test 93: Mobile Performance ─────────────────────────────────

export const MOBILE_TEST: PerformanceTestConfig = {
  name: 'Mobile Performance',
  url: '/',
  device: 'mobile',
  runs: 3,
  targets: {
    performance: 85,
    lcp: 3000,
    fcp: 2000,
    cls: 0.1,
    fid: 100,
    tti: 5000,
  },
  checks: [
    'Touch targets >= 48px',
    'No horizontal scroll',
    'Font sizes readable without zoom',
    'Images responsive and optimized',
    'Viewport meta tag correct',
    'Tested on 3G throttling',
  ],
};

/** All test configs */
export const ALL_PERFORMANCE_TESTS = [
  HOMEPAGE_TEST,
  PRODUCT_PAGE_TEST,
  CATEGORY_PAGE_TEST,
  MOBILE_TEST,
] as const;
