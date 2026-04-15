/**
 * Storefront Query Key Factory
 *
 * Structured query-key factories for the customer-facing webstore.
 * Uses 'store-' prefix to differentiate from dashboard query keys.
 */

export interface StoreProductFilters {
  category?: string;
  search?: string;
  priceMin?: number;
  priceMax?: number;
  sort?: 'newest' | 'price-asc' | 'price-desc' | 'popularity' | 'rating';
  page?: number;
  limit?: number;
  inStock?: boolean;
  featured?: boolean;
  onSale?: boolean;
}

export interface StoreCategoryFilters {
  parentId?: number;
  includeSubcategories?: boolean;
}

export const storeQueryKeys = {
  products: {
    all: () => ['store-products'] as const,
    list: (filters?: StoreProductFilters) => ['store-products', 'list', filters] as const,
    detail: (slug: string) => ['store-products', 'detail', slug] as const,
    featured: (limit?: number) => ['store-products', 'featured', limit] as const,
    sale: (limit?: number) => ['store-products', 'sale', limit] as const,
    related: (id: number, limit?: number) => ['store-products', 'related', id, limit] as const,
    search: (query: string, filters?: StoreProductFilters) =>
      ['store-products', 'search', query, filters] as const,
    availability: (ids: number[]) => ['store-products', 'availability', ids] as const,
    variants: (id: number) => ['store-products', 'variants', id] as const,
    reviews: (id: number) => ['store-products', 'reviews', id] as const,
    reviewStats: (id: number) => ['store-products', 'review-stats', id] as const,
  },
  categories: {
    all: () => ['store-categories'] as const,
    list: (filters?: StoreCategoryFilters) => ['store-categories', 'list', filters] as const,
    detail: (slug: string) => ['store-categories', 'detail', slug] as const,
    tree: () => ['store-categories', 'tree'] as const,
    featured: () => ['store-categories', 'featured'] as const,
    products: (slug: string, filters?: StoreProductFilters) =>
      ['store-categories', 'products', slug, filters] as const,
    breadcrumb: (id: number) => ['store-categories', 'breadcrumb', id] as const,
    filters: (slug: string) => ['store-categories', 'filters', slug] as const,
  },
  cart: {
    all: () => ['store-cart'] as const,
    current: () => ['store-cart', 'current'] as const,
  },
  wishlist: {
    all: () => ['store-wishlist'] as const,
    current: () => ['store-wishlist', 'current'] as const,
  },
  orders: {
    all: () => ['store-orders'] as const,
    list: (filters?: Record<string, unknown>) => ['store-orders', 'list', filters] as const,
    detail: (id: number) => ['store-orders', 'detail', id] as const,
    tracking: (id: number) => ['store-orders', 'tracking', id] as const,
  },
  customer: {
    profile: () => ['store-customer', 'profile'] as const,
    addresses: () => ['store-customer', 'addresses'] as const,
    preferences: () => ['store-customer', 'preferences'] as const,
    reviews: () => ['store-customer', 'reviews'] as const,
  },
  search: {
    results: (query: string, filters?: Record<string, unknown>) =>
      ['store-search', query, filters] as const,
    suggestions: (query: string) => ['store-search', 'suggestions', query] as const,
    facets: () => ['store-search', 'facets'] as const,
    history: () => ['store-search', 'history'] as const,
  },
};
