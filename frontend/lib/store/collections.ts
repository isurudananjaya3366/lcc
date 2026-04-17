/**
 * Collection Data Fetching Utilities (Task 81)
 *
 * Server-side functions for fetching collection information,
 * curated products, related collections, and featured collections.
 */

import type { BreadcrumbItem } from '@/components/storefront/catalog/Breadcrumb';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

// ── Types ──────────────────────────────────────────────────

export interface StoreCollection {
  id: string;
  name: string;
  slug: string;
  description: string;
  story?: string;
  heroImage?: string;
  thumbnailImage?: string;
  curatedBy?: string | null;
  tags: string[];
  featured: boolean;
  productCount: number;
  createdAt: string;
}

export interface FeaturedCollection {
  id: string;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  productCount: number;
}

// ── getCollectionBySlug ────────────────────────────────────

export async function getCollectionBySlug(slug: string): Promise<StoreCollection | null> {
  try {
    const res = await fetch(`${API_BASE}/store/collections/${slug}`, {
      next: { revalidate: 600, tags: [`collection-${slug}`] },
    });
    if (!res.ok) return null;
    return (await res.json()) as StoreCollection;
  } catch {
    return null;
  }
}

// ── getRelatedCollections ──────────────────────────────────

export async function getRelatedCollections(
  collectionId: string,
  limit = 4
): Promise<FeaturedCollection[]> {
  try {
    const res = await fetch(
      `${API_BASE}/store/collections/${collectionId}/related?limit=${limit}`,
      { next: { revalidate: 600, tags: ['collections'] } }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results ?? data) as FeaturedCollection[];
  } catch {
    return [];
  }
}

// ── getFeaturedCollections ─────────────────────────────────

export async function getFeaturedCollections(limit = 6): Promise<FeaturedCollection[]> {
  try {
    const res = await fetch(`${API_BASE}/store/collections?featured=true&limit=${limit}`, {
      next: { revalidate: 300, tags: ['featured-collections'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results ?? data) as FeaturedCollection[];
  } catch {
    return [];
  }
}

// ── getAllCollections ───────────────────────────────────────

export async function getAllCollections(params?: {
  page?: number;
  limit?: number;
}): Promise<{ collections: FeaturedCollection[]; total: number }> {
  try {
    const page = params?.page ?? 1;
    const limit = params?.limit ?? 12;
    const res = await fetch(`${API_BASE}/store/collections?page=${page}&limit=${limit}`, {
      next: { revalidate: 300, tags: ['collections'] },
    });
    if (!res.ok) return { collections: [], total: 0 };
    const data = await res.json();
    return {
      collections: (data.results ?? data) as FeaturedCollection[],
      total: data.count ?? 0,
    };
  } catch {
    return { collections: [], total: 0 };
  }
}

// ── getCollectionBreadcrumbs ───────────────────────────────

export function getCollectionBreadcrumbs(collection: StoreCollection): BreadcrumbItem[] {
  return [
    { label: 'Home', href: '/', current: false },
    { label: 'Collections', href: '/products', current: false },
    { label: collection.name, current: true },
  ];
}
