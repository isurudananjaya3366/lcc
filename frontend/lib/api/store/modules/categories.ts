import { getStoreClient, type PaginatedResponse } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Category {
  id: number;
  slug: string;
  name: string;
  description: string;
  parent_id: number | null;
  level: number;
  image_url: string | null;
  product_count: number;
  is_active: boolean;
  order: number;
}

export interface CategoryTree extends Category {
  children: CategoryTree[];
}

export interface CategoriesListParams {
  parent_id?: number;
  include_products?: boolean;
  ordering?: string;
}

// ─── Cache ──────────────────────────────────────────────────────────────────

const cache = new Map<string, { data: unknown; expiry: number }>();
const CACHE_TTL = 10 * 60 * 1000; // 10 minutes (stable data)

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
  cache.set(key, { data, expiry: Date.now() + CACHE_TTL });
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function getCategories(params?: CategoriesListParams): Promise<Category[]> {
  const cacheKey = `categories-${JSON.stringify(params || {})}`;
  const cached = getCached<Category[]>(cacheKey);
  if (cached) return cached;

  const { data } = await getStoreClient().get('/categories/', { params });
  const result = data.results ?? data;
  setCache(cacheKey, result);
  return result;
}

export async function getCategoriesTree(): Promise<CategoryTree[]> {
  const cacheKey = 'categories-tree';
  const cached = getCached<CategoryTree[]>(cacheKey);
  if (cached) return cached;

  const { data } = await getStoreClient().get('/categories/', { params: { flat: false } });
  const result = data.results ?? data;
  setCache(cacheKey, result);
  return result;
}

export async function getCategory(slug: string): Promise<Category> {
  const cacheKey = `category-${slug}`;
  const cached = getCached<Category>(cacheKey);
  if (cached) return cached;

  const { data } = await getStoreClient().get(`/categories/${slug}/`);
  setCache(cacheKey, data);
  return data;
}

export async function getCategoryProducts(
  slug: string,
  params?: { page?: number; page_size?: number; sort?: string; order?: 'asc' | 'desc' }
): Promise<PaginatedResponse<import('./products').Product>> {
  const { data } = await getStoreClient().get(`/categories/${slug}/products/`, { params });
  return data;
}

export async function getCategoryBreadcrumb(categoryId: number): Promise<Category[]> {
  const categories = await getCategories();
  const breadcrumb: Category[] = [];
  let current = categories.find((c) => c.id === categoryId);

  while (current) {
    breadcrumb.unshift(current);
    current = current.parent_id ? categories.find((c) => c.id === current!.parent_id) : undefined;
  }

  return breadcrumb;
}

export async function getSubcategories(parentId: number): Promise<Category[]> {
  return getCategories({ parent_id: parentId });
}

const categoriesApi = {
  getCategories,
  getCategoriesTree,
  getCategory,
  getCategoryProducts,
  getCategoryBreadcrumb,
  getSubcategories,
};

export default categoriesApi;
