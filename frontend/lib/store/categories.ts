/**
 * Category Data Fetching Utilities (Task 76)
 *
 * Server-side functions for fetching category information,
 * subcategories, and building breadcrumbs.
 */

import type { StoreCategory, StoreCategoryBreadcrumb } from '@/types/store/category';
import type { BreadcrumbItem } from '@/components/storefront/catalog/Breadcrumb';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

// ── getCategoryBySlug ──────────────────────────────────────

export async function getCategoryBySlug(slug: string): Promise<StoreCategory | null> {
  try {
    const res = await fetch(`${API_BASE}/store/categories/${slug}`, {
      next: { revalidate: 600, tags: [`category-${slug}`] },
    });
    if (!res.ok) return null;
    return (await res.json()) as StoreCategory;
  } catch {
    return null;
  }
}

// ── getSubcategories ───────────────────────────────────────

export async function getSubcategories(parentId: string): Promise<StoreCategory[]> {
  try {
    const res = await fetch(`${API_BASE}/store/categories?parent_id=${parentId}&is_visible=true`, {
      next: { revalidate: 600, tags: ['categories'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results ?? data) as StoreCategory[];
  } catch {
    return [];
  }
}

// ── getCategoryBreadcrumbs ─────────────────────────────────

export function getCategoryBreadcrumbs(
  category: StoreCategory,
  ancestors?: StoreCategoryBreadcrumb[]
): BreadcrumbItem[] {
  const items: BreadcrumbItem[] = [
    { label: 'Home', href: '/', current: false },
    { label: 'Products', href: '/products', current: false },
  ];

  if (ancestors?.length) {
    for (const a of ancestors) {
      items.push({
        label: a.name,
        href: `/products/category/${a.slug}`,
        current: false,
      });
    }
  }

  items.push({ label: category.name, current: true });
  return items;
}

// ── getCategoryTree ────────────────────────────────────────

export async function getCategoryTree(): Promise<StoreCategory[]> {
  try {
    const res = await fetch(`${API_BASE}/store/categories/tree`, {
      next: { revalidate: 600, tags: ['category-tree'] },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results ?? data) as StoreCategory[];
  } catch {
    return [];
  }
}
