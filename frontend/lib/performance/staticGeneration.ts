/**
 * Static Generation Helpers
 *
 * Functions for generating static params, fetching build-time data,
 * and managing ISR revalidation.
 */

import { REVALIDATE_TIMES } from './staticConfig';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ── generateStaticParams Helpers ────────────────────────────────

/** Fetch product slugs for static generation (top 100) */
export async function getProductStaticParams(): Promise<{ slug: string }[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/store/products/?limit=100&ordering=-created_on`, {
      next: { revalidate: REVALIDATE_TIMES.products },
    });
    if (!res.ok) return [];
    const data = await res.json();
    const results = Array.isArray(data) ? data : data.results ?? [];
    return results.map((p: { slug: string }) => ({ slug: p.slug }));
  } catch {
    return [];
  }
}

/** Fetch category slugs for static generation */
export async function getCategoryStaticParams(): Promise<{ slug: string }[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/store/categories/`, {
      next: { revalidate: REVALIDATE_TIMES.categories },
    });
    if (!res.ok) return [];
    const data = await res.json();
    const results = Array.isArray(data) ? data : data.results ?? [];
    return results.map((c: { slug: string }) => ({ slug: c.slug }));
  } catch {
    return [];
  }
}

/** Fetch collection slugs for static generation */
export async function getCollectionStaticParams(): Promise<{ slug: string }[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/store/collections/`, {
      next: { revalidate: REVALIDATE_TIMES.collections },
    });
    if (!res.ok) return [];
    const data = await res.json();
    const results = Array.isArray(data) ? data : data.results ?? [];
    return results.map((c: { slug: string }) => ({ slug: c.slug }));
  } catch {
    return [];
  }
}

/** Fetch blog post slugs for static generation */
export async function getBlogStaticParams(): Promise<{ slug: string }[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/store/blog/posts/`, {
      next: { revalidate: REVALIDATE_TIMES.blog },
    });
    if (!res.ok) return [];
    const data = await res.json();
    const results = Array.isArray(data) ? data : data.results ?? [];
    return results.map((p: { slug: string }) => ({ slug: p.slug }));
  } catch {
    return [];
  }
}

// ── Build-time Data Fetching ────────────────────────────────────

/** Fetch homepage data at build time (Task 54, 66) */
export async function getHomepageData() {
  try {
    const [featuredRes, categoriesRes] = await Promise.all([
      fetch(`${API_BASE}/api/v1/store/products/?featured=true&limit=8`, {
        next: { revalidate: REVALIDATE_TIMES.homepage },
      }),
      fetch(`${API_BASE}/api/v1/store/categories/?limit=12`, {
        next: { revalidate: REVALIDATE_TIMES.categories },
      }),
    ]);

    const featured = featuredRes.ok ? await featuredRes.json() : { results: [] };
    const categories = categoriesRes.ok ? await categoriesRes.json() : { results: [] };

    return {
      featuredProducts: featured.results ?? featured ?? [],
      categories: categories.results ?? categories ?? [],
    };
  } catch {
    return { featuredProducts: [], categories: [] };
  }
}
