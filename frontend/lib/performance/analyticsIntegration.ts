/**
 * Performance Analytics Integration
 *
 * Reports Web Vitals to Google Analytics 4 and/or custom endpoint.
 * Includes batching, throttling, and sampling for high traffic.
 */

import type { WebVitalMetric } from './webVitals';

// ── Configuration ───────────────────────────────────────────────

const ANALYTICS_CONFIG = {
  /** Custom analytics endpoint */
  endpoint: process.env.NEXT_PUBLIC_ANALYTICS_ENDPOINT || '',

  /** GA4 Measurement ID */
  ga4MeasurementId: process.env.NEXT_PUBLIC_GA4_ID || '',

  /** Batch size before flush */
  batchSize: 10,

  /** Max wait before flush (ms) */
  flushInterval: 5000,

  /** Sampling rate (0-1): 1 = all traffic, 0.1 = 10% */
  samplingRate: parseFloat(process.env.NEXT_PUBLIC_PERF_SAMPLING || '1'),
} as const;

// ── Metric Queue ────────────────────────────────────────────────

let metricQueue: WebVitalMetric[] = [];
let flushTimer: ReturnType<typeof setTimeout> | null = null;

/** Add metric to batch queue */
export function reportToAnalytics(metric: WebVitalMetric): void {
  // Apply sampling
  if (Math.random() > ANALYTICS_CONFIG.samplingRate) return;

  metricQueue.push(metric);

  // Report to GA4 if available
  reportToGA4(metric);

  // Batch and flush to custom endpoint
  if (metricQueue.length >= ANALYTICS_CONFIG.batchSize) {
    flushMetrics();
  } else if (!flushTimer) {
    flushTimer = setTimeout(flushMetrics, ANALYTICS_CONFIG.flushInterval);
  }
}

/** Flush queued metrics to analytics endpoint */
async function flushMetrics(): Promise<void> {
  if (flushTimer) {
    clearTimeout(flushTimer);
    flushTimer = null;
  }

  if (metricQueue.length === 0) return;

  const batch = [...metricQueue];
  metricQueue = [];

  if (!ANALYTICS_CONFIG.endpoint) return;

  try {
    // Use sendBeacon for reliability during page unload
    const payload = JSON.stringify({
      metrics: batch.map((m) => ({
        name: m.name,
        value: m.value,
        rating: m.rating,
        delta: m.delta,
        id: m.id,
        page: typeof window !== 'undefined' ? window.location.pathname : '',
        timestamp: Date.now(),
      })),
    });

    if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
      navigator.sendBeacon(ANALYTICS_CONFIG.endpoint, payload);
    } else {
      await fetch(ANALYTICS_CONFIG.endpoint, {
        method: 'POST',
        body: payload,
        headers: { 'Content-Type': 'application/json' },
        keepalive: true,
      });
    }
  } catch {
    // Silent fail — analytics should never break the app
  }
}

/** Report to Google Analytics 4 */
function reportToGA4(metric: WebVitalMetric): void {
  if (typeof window === 'undefined') return;
  const gtag = (window as Window & { gtag?: (...args: unknown[]) => void }).gtag;
  if (!gtag) return;

  gtag('event', metric.name, {
    value: Math.round(metric.name === 'CLS' ? metric.delta * 1000 : metric.delta),
    event_category: 'Web Vitals',
    event_label: metric.id,
    non_interaction: true,
  });
}

// ── Flush on page unload ────────────────────────────────────────

if (typeof window !== 'undefined') {
  window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      flushMetrics();
    }
  });
}
