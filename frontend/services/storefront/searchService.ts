/**
 * Storefront Search Service
 *
 * Provides search functionality for the storefront autocomplete.
 * Uses plain fetch() against the store API endpoints.
 */

const STORE_API_URL = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/store`;

// ─── Types ──────────────────────────────────────────────────────────────────

export interface SearchProduct {
  id: string;
  slug: string;
  name: string;
  description: string;
  price: number;
  sale_price: number | null;
  currency: string;
  in_stock: boolean;
  sku: string;
  category: { id: string; slug: string; name: string };
  images: { id: string; url: string; alt_text: string; is_primary: boolean; order: number }[];
  rating: number;
  review_count: number;
}

export interface SearchCategory {
  id: string;
  slug: string;
  name: string;
}

export interface SearchSuggestionsResult {
  products: SearchProduct[];
  categories: SearchCategory[];
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function searchProducts(
  query: string,
  limit: number = 5
): Promise<{ results: SearchProduct[]; count: number }> {
  try {
    const params = new URLSearchParams({
      search: query,
      page_size: String(limit),
    });
    const res = await fetch(`${STORE_API_URL}/products/?${params.toString()}`);
    if (!res.ok) return { results: [], count: 0 };
    const data = await res.json();
    return { results: data.results ?? [], count: data.count ?? 0 };
  } catch {
    return { results: [], count: 0 };
  }
}

export async function searchCategories(query: string): Promise<SearchCategory[]> {
  try {
    const res = await fetch(
      `${STORE_API_URL}/categories/?search=${encodeURIComponent(query)}`
    );
    if (!res.ok) return [];
    const data = await res.json();
    const categories: SearchCategory[] = data.results ?? data ?? [];
    return categories.slice(0, 5);
  } catch {
    return [];
  }
}

export async function getSearchSuggestions(query: string): Promise<SearchSuggestionsResult> {
  const [productData, categories] = await Promise.all([
    searchProducts(query, 5),
    searchCategories(query),
  ]);
  return { products: productData.results, categories };
}
