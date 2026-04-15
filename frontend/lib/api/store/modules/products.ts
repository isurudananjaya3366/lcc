import { getStoreClient, type PaginatedResponse } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ProductImage {
  id: number;
  url: string;
  alt_text: string;
  is_primary: boolean;
  order: number;
}

export interface ProductVariant {
  id: number;
  name: string;
  sku: string;
  price: number;
  in_stock: boolean;
  attributes: Record<string, string>;
}

export interface ProductReview {
  id: number;
  user_name: string;
  rating: number;
  title: string;
  comment: string;
  created_at: string;
  verified_purchase: boolean;
}

export interface Product {
  id: number;
  slug: string;
  name: string;
  description: string;
  price: number;
  sale_price: number | null;
  currency: string;
  in_stock: boolean;
  stock_quantity: number;
  sku: string;
  category: { id: number; slug: string; name: string } | null;
  images: ProductImage[];
  variants: ProductVariant[];
  rating: number;
  review_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProductsListParams {
  page?: number;
  page_size?: number;
  search?: string;
  category?: string;
  min_price?: number;
  max_price?: number;
  sort?: string;
  order?: 'asc' | 'desc';
  in_stock?: boolean;
  featured?: boolean;
  on_sale?: boolean;
}

// ─── Cache ──────────────────────────────────────────────────────────────────

const cache = new Map<string, { data: unknown; expiry: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes
const MAX_CACHE_ENTRIES = 100;

function getCached<T>(key: string): T | null {
  const entry = cache.get(key);
  if (!entry) return null;
  if (Date.now() > entry.expiry) {
    cache.delete(key);
    return null;
  }
  return entry.data as T;
}

function setCache(key: string, data: unknown): void {
  if (cache.size >= MAX_CACHE_ENTRIES) {
    const firstKey = cache.keys().next().value;
    if (firstKey) cache.delete(firstKey);
  }
  cache.set(key, { data, expiry: Date.now() + CACHE_TTL });
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function getProducts(
  params?: ProductsListParams
): Promise<PaginatedResponse<Product>> {
  const { data } = await getStoreClient().get('/products/', { params });
  return data;
}

export async function getProduct(slug: string): Promise<Product> {
  const cacheKey = `product-${slug}`;
  const cached = getCached<Product>(cacheKey);
  if (cached) return cached;

  const { data } = await getStoreClient().get(`/products/${slug}/`);
  setCache(cacheKey, data);
  return data;
}

export async function getProductVariants(productId: number): Promise<ProductVariant[]> {
  const { data } = await getStoreClient().get(`/products/${productId}/variants/`);
  return data;
}

export async function getProductReviews(
  productId: number,
  params?: { page?: number; page_size?: number }
): Promise<PaginatedResponse<ProductReview>> {
  const { data } = await getStoreClient().get(`/products/${productId}/reviews/`, { params });
  return data;
}

export async function searchProducts(
  query: string,
  params?: Omit<ProductsListParams, 'search'>
): Promise<PaginatedResponse<Product>> {
  const { data } = await getStoreClient().get('/products/', {
    params: { search: query, ...params },
  });
  return data;
}

export async function getFeaturedProducts(limit?: number): Promise<Product[]> {
  const { data } = await getStoreClient().get('/products/', {
    params: { featured: true, page_size: limit || 8 },
  });
  return data.results ?? data;
}

export async function getRelatedProducts(productId: number, limit?: number): Promise<Product[]> {
  const { data } = await getStoreClient().get(`/products/${productId}/related/`, {
    params: { limit: limit || 4 },
  });
  return data.results ?? data;
}

export async function getVariantByAttributes(
  productId: number,
  attributes: Record<string, string>
): Promise<ProductVariant | null> {
  const variants = await getProductVariants(productId);
  return (
    variants.find((v) =>
      Object.entries(attributes).every(([key, value]) => v.attributes[key] === value)
    ) ?? null
  );
}

const productsApi = {
  getProducts,
  getProduct,
  getProductVariants,
  getProductReviews,
  searchProducts,
  getFeaturedProducts,
  getRelatedProducts,
  getVariantByAttributes,
};

export default productsApi;
