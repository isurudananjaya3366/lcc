/**
 * Static Generation & ISR Configuration
 *
 * Centralized revalidation times and page generation strategy.
 */

// ── Revalidation Times (seconds) ────────────────────────────────

export const REVALIDATE_TIMES = {
  /** Homepage — refresh every hour */
  homepage: 3600,         // 1 hour

  /** Product pages — ISR, refresh hourly */
  products: 3600,         // 1 hour

  /** Category pages — less volatile */
  categories: 21600,      // 6 hours

  /** Blog posts — rarely change */
  blog: 86400,            // 24 hours

  /** CMS/static pages */
  cms: 43200,             // 12 hours

  /** Collection pages */
  collections: 21600,     // 6 hours

  /** Search results — always dynamic */
  search: 0,              // No caching (dynamic)

  /** Cart/checkout — always dynamic */
  cart: 0,
  checkout: 0,
} as const;

// ── Page Generation Strategy ────────────────────────────────────

export type GenerationStrategy = 'static' | 'isr' | 'ssr' | 'client';

export interface PageConfig {
  route: string;
  strategy: GenerationStrategy;
  revalidate?: number;
  generateStaticParams?: boolean;
  notes?: string;
}

export const PAGE_STRATEGIES: PageConfig[] = [
  { route: '/', strategy: 'isr', revalidate: REVALIDATE_TIMES.homepage, notes: 'Featured products change' },
  { route: '/products', strategy: 'isr', revalidate: REVALIDATE_TIMES.products },
  { route: '/products/[slug]', strategy: 'isr', revalidate: REVALIDATE_TIMES.products, generateStaticParams: true },
  { route: '/collections/[slug]', strategy: 'isr', revalidate: REVALIDATE_TIMES.collections, generateStaticParams: true },
  { route: '/blog', strategy: 'isr', revalidate: REVALIDATE_TIMES.blog },
  { route: '/blog/[slug]', strategy: 'isr', revalidate: REVALIDATE_TIMES.blog, generateStaticParams: true },
  { route: '/pages/about', strategy: 'static', revalidate: REVALIDATE_TIMES.cms },
  { route: '/pages/contact', strategy: 'static', revalidate: REVALIDATE_TIMES.cms },
  { route: '/pages/faq', strategy: 'isr', revalidate: REVALIDATE_TIMES.cms },
  { route: '/pages/terms', strategy: 'static', revalidate: REVALIDATE_TIMES.cms },
  { route: '/pages/privacy', strategy: 'static', revalidate: REVALIDATE_TIMES.cms },
  { route: '/pages/returns', strategy: 'static', revalidate: REVALIDATE_TIMES.cms },
  { route: '/pages/shipping', strategy: 'static', revalidate: REVALIDATE_TIMES.cms },
  { route: '/search', strategy: 'client', notes: 'Search is always client-rendered' },
  { route: '/cart', strategy: 'client', notes: 'Cart is per-user' },
  { route: '/checkout', strategy: 'client', notes: 'Checkout is per-session' },
  { route: '/account/*', strategy: 'ssr', notes: 'Auth-protected, server-rendered' },
  { route: '/dashboard/*', strategy: 'ssr', notes: 'Admin pages, server-rendered' },
];
