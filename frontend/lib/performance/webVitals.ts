/**
 * Core Web Vitals Tracking
 *
 * Uses the web-vitals library to track LCP, FID/INP, CLS, FCP, TTFB.
 * Metrics are reported to analytics and optionally to a custom endpoint.
 */

export interface WebVitalMetric {
  name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB' | 'INP';
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  id: string;
  navigationType: string;
  entries: PerformanceEntry[];
}

// ── Thresholds ──────────────────────────────────────────────────

export const WEB_VITAL_THRESHOLDS = {
  LCP: { good: 2500, poor: 4000 },
  FID: { good: 100, poor: 300 },
  CLS: { good: 0.1, poor: 0.25 },
  FCP: { good: 1800, poor: 3000 },
  TTFB: { good: 800, poor: 1800 },
  INP: { good: 200, poor: 500 },
} as const;

// ── Per-page Targets ────────────────────────────────────────────

export const PAGE_TARGETS = {
  homepage: { LCP: 2000, FCP: 1500, CLS: 0.05 },
  productDetail: { LCP: 2200, FCP: 1500, CLS: 0.08 },
  productListing: { LCP: 2500, FCP: 1800, CLS: 0.1 },
  cart: { LCP: 2000, FCP: 1200, CLS: 0.05 },
  checkout: { LCP: 2500, FCP: 1500, CLS: 0.05 },
  blog: { LCP: 2200, FCP: 1500, CLS: 0.05 },
} as const;

// ── Metric Collection ───────────────────────────────────────────

type MetricHandler = (metric: WebVitalMetric) => void;

const handlers: MetricHandler[] = [];

/** Register a handler for all web vital metrics */
export function onWebVital(handler: MetricHandler): void {
  handlers.push(handler);
}

/** Internal dispatch to all handlers */
function reportMetric(metric: WebVitalMetric): void {
  handlers.forEach((handler) => {
    try {
      handler(metric);
    } catch (e) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[WebVitals] Handler error:', e);
      }
    }
  });
}

// ── LCP Monitoring (Task 86) ────────────────────────────────────

export function trackLCP(metric: WebVitalMetric): void {
  const lcpEntry = metric.entries[metric.entries.length - 1] as PerformanceEntry & {
    element?: Element;
    url?: string;
  };

  const details = {
    ...metric,
    element: lcpEntry?.element?.tagName || 'unknown',
    url: (lcpEntry as { url?: string })?.url || '',
    pageType: getPageType(),
  };

  reportMetric(details as unknown as WebVitalMetric);

  if (process.env.NODE_ENV === 'development') {
    const status = metric.value <= WEB_VITAL_THRESHOLDS.LCP.good ? 'GOOD' : 'NEEDS WORK';
    console.log(`[LCP] ${metric.value.toFixed(0)}ms — ${status}`);
  }
}

// ── FID/INP Monitoring (Task 87) ────────────────────────────────

export function trackFID(metric: WebVitalMetric): void {
  reportMetric(metric);

  if (process.env.NODE_ENV === 'development') {
    const status = metric.value <= WEB_VITAL_THRESHOLDS.FID.good ? 'GOOD' : 'NEEDS WORK';
    console.log(`[FID] ${metric.value.toFixed(0)}ms — ${status}`);
  }
}

export function trackINP(metric: WebVitalMetric): void {
  reportMetric(metric);

  if (process.env.NODE_ENV === 'development') {
    const status = metric.value <= WEB_VITAL_THRESHOLDS.INP.good ? 'GOOD' : 'NEEDS WORK';
    console.log(`[INP] ${metric.value.toFixed(0)}ms — ${status}`);
  }
}

// ── CLS Monitoring (Task 88) ────────────────────────────────────

export function trackCLS(metric: WebVitalMetric): void {
  const clsEntries = metric.entries as (PerformanceEntry & {
    sources?: Array<{ node?: Node }>;
  })[];

  const sources = clsEntries
    .flatMap((entry) => entry.sources ?? [])
    .map((source) => {
      const node = source.node;
      if (node instanceof Element) {
        return node.tagName + (node.id ? `#${node.id}` : '') + (node.className ? `.${String(node.className).split(' ')[0]}` : '');
      }
      return 'unknown';
    });

  reportMetric({ ...metric, entries: metric.entries });

  if (process.env.NODE_ENV === 'development') {
    const status = metric.value <= WEB_VITAL_THRESHOLDS.CLS.good ? 'GOOD' : 'NEEDS WORK';
    console.log(`[CLS] ${metric.value.toFixed(3)} — ${status}`, sources.length > 0 ? `Sources: ${sources.join(', ')}` : '');
  }
}

// ── Initialize Tracking ─────────────────────────────────────────

export async function initWebVitals(): Promise<void> {
  if (typeof window === 'undefined') return;

  try {
    const { onCLS, onFID, onLCP, onFCP, onTTFB, onINP } = await import('web-vitals');

    onCLS(trackCLS as Parameters<typeof onCLS>[0]);
    onFID(trackFID as Parameters<typeof onFID>[0]);
    onLCP(trackLCP as Parameters<typeof onLCP>[0]);
    onFCP(reportMetric as Parameters<typeof onFCP>[0]);
    onTTFB(reportMetric as Parameters<typeof onTTFB>[0]);
    onINP(trackINP as Parameters<typeof onINP>[0]);
  } catch {
    // web-vitals not available
  }
}

// ── Helpers ─────────────────────────────────────────────────────

function getPageType(): string {
  if (typeof window === 'undefined') return 'unknown';
  const path = window.location.pathname;
  if (path === '/') return 'homepage';
  if (path.startsWith('/products/')) return 'productDetail';
  if (path === '/products') return 'productListing';
  if (path === '/cart') return 'cart';
  if (path.startsWith('/checkout')) return 'checkout';
  if (path.startsWith('/blog')) return 'blog';
  return 'other';
}
