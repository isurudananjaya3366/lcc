/**
 * Product Data Fetching Utilities (Phase-08 SP04 Group A)
 *
 * Server-side functions for fetching product information
 * and building breadcrumbs for the product detail page.
 */

import type { Product } from '@/lib/api/store/modules/products';
import type { BreadcrumbItem } from '@/components/storefront/catalog/Breadcrumb';

const STORE_API = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

// ── getProductBySlug ───────────────────────────────────────

export async function getProductBySlug(slug: string): Promise<Product | null> {
  try {
    const res = await fetch(`${STORE_API}/products/${slug}/`, {
      next: { revalidate: 3600, tags: [`product-${slug}`] },
    });
    if (!res.ok) return null;
    return (await res.json()) as Product;
  } catch {
    return null;
  }
}

// ── getRelatedProductsBySlug ───────────────────────────────

export async function getRelatedProductsBySlug(
  slug: string,
  limit: number = 4
): Promise<Product[]> {
  try {
    const product = await getProductBySlug(slug);
    if (!product) return [];

    const res = await fetch(
      `${STORE_API}/products/${product.id}/related/?limit=${limit}`,
      {
        next: { revalidate: 3600, tags: [`product-${slug}-related`] },
      }
    );
    if (!res.ok) return [];
    const data = await res.json();
    return (data.results ?? data) as Product[];
  } catch {
    return [];
  }
}

// ── getProductBreadcrumbs ──────────────────────────────────

export function getProductBreadcrumbs(product: Product): BreadcrumbItem[] {
  const items: BreadcrumbItem[] = [
    { label: 'Home', href: '/', current: false },
    { label: 'Products', href: '/products', current: false },
  ];

  if (product.category) {
    items.push({
      label: product.category.name,
      href: `/products/category/${product.category.slug}`,
      current: false,
    });
  }

  items.push({ label: product.name, current: true });
  return items;
}
