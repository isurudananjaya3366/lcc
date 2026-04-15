'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { storeQueryKeys, type StoreProductFilters } from '@/lib/storeQueryKeys';
import {
  getProducts,
  getProduct,
  getFeaturedProducts,
  getRelatedProducts,
  searchProducts,
  getProductVariants,
  getProductReviews,
} from '@/lib/api/store/modules/products';
import { getReviewStats } from '@/lib/api/store/modules/reviews';
import { getStoreClient } from '@/lib/api/store/client';

// ─── useProducts ────────────────────────────────────────────────────────────

export function useProducts(filters?: StoreProductFilters) {
  return useQuery({
    queryKey: storeQueryKeys.products.list(filters),
    queryFn: () =>
      getProducts({
        page: filters?.page,
        page_size: filters?.limit,
        search: filters?.search,
        category: filters?.category,
        min_price: filters?.priceMin,
        max_price: filters?.priceMax,
        sort: filters?.sort,
        in_stock: filters?.inStock,
        featured: filters?.featured,
        on_sale: filters?.onSale,
      }),
    staleTime: 5 * 60 * 1000,
  });
}

// ─── useProduct ─────────────────────────────────────────────────────────────

export function useProduct(slug: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: storeQueryKeys.products.detail(slug),
    queryFn: () => getProduct(slug),
    enabled: options?.enabled ?? !!slug,
    staleTime: 5 * 60 * 1000,
  });
}

// ─── useFeaturedProducts ────────────────────────────────────────────────────

export function useFeaturedProducts(limit: number = 8) {
  return useQuery({
    queryKey: storeQueryKeys.products.featured(limit),
    queryFn: () => getFeaturedProducts(limit),
    staleTime: 10 * 60 * 1000,
  });
}

// ─── useSaleProducts ────────────────────────────────────────────────────────

export function useSaleProducts(limit: number = 12) {
  return useQuery({
    queryKey: storeQueryKeys.products.sale(limit),
    queryFn: () => getProducts({ on_sale: true, page_size: limit }).then((res) => res.results),
    staleTime: 2 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
  });
}

// ─── useRelatedProducts ─────────────────────────────────────────────────────

export function useRelatedProducts(productId: number, limit: number = 6) {
  return useQuery({
    queryKey: storeQueryKeys.products.related(productId, limit),
    queryFn: () => getRelatedProducts(productId, limit),
    enabled: !!productId,
    refetchOnWindowFocus: false,
  });
}

// ─── useProductSearch ───────────────────────────────────────────────────────

export function useProductSearch(query: string, filters?: StoreProductFilters) {
  return useQuery({
    queryKey: storeQueryKeys.products.search(query, filters),
    queryFn: () => searchProducts(query, filters),
    enabled: query.length >= 3,
    staleTime: 1 * 60 * 1000,
  });
}

// ─── useProductVariants ─────────────────────────────────────────────────────

export function useProductVariants(productId: number) {
  return useQuery({
    queryKey: storeQueryKeys.products.variants(productId),
    queryFn: () => getProductVariants(productId),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000,
  });
}

// ─── useProductReviews ──────────────────────────────────────────────────────

export function useProductReviews(
  productId: number,
  params?: { page?: number; page_size?: number }
) {
  return useQuery({
    queryKey: storeQueryKeys.products.reviews(productId),
    queryFn: () => getProductReviews(productId, params),
    enabled: !!productId,
  });
}

// ─── useReviewStats ─────────────────────────────────────────────────────────

export function useReviewStats(productId: number) {
  return useQuery({
    queryKey: storeQueryKeys.products.reviewStats(productId),
    queryFn: () => getReviewStats(productId),
    enabled: !!productId,
    staleTime: 5 * 60 * 1000,
  });
}

// ─── useProductAvailability ─────────────────────────────────────────────────

export interface ProductAvailability {
  productId: number;
  inStock: boolean;
  quantity: number;
}

export function useProductAvailability(productIds: number[]) {
  return useQuery({
    queryKey: storeQueryKeys.products.availability(productIds),
    queryFn: async (): Promise<Map<number, boolean>> => {
      const { data } = await getStoreClient().post('/products/availability/', {
        product_ids: productIds,
      });
      const map = new Map<number, boolean>();
      for (const item of data as ProductAvailability[]) {
        map.set(item.productId, item.inStock);
      }
      return map;
    },
    enabled: productIds.length > 0,
    staleTime: 30 * 1000, // 30 seconds — near-real-time stock
    refetchInterval: 60 * 1000, // refetch every 60 seconds
  });
}

// ─── useProductMutations ────────────────────────────────────────────────────

export function useProductMutations() {
  const qc = useQueryClient();

  const addProduct = useMutation({
    mutationFn: (product: Record<string, unknown>) =>
      getStoreClient()
        .post('/products/', product)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: storeQueryKeys.products.all() });
    },
  });

  const updateProduct = useMutation({
    mutationFn: ({ slug, data }: { slug: string; data: Record<string, unknown> }) =>
      getStoreClient()
        .patch(`/products/${slug}/`, data)
        .then((r) => r.data),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: storeQueryKeys.products.detail(variables.slug) });
      qc.invalidateQueries({ queryKey: storeQueryKeys.products.all() });
    },
  });

  const deleteProduct = useMutation({
    mutationFn: (slug: string) =>
      getStoreClient()
        .delete(`/products/${slug}/`)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: storeQueryKeys.products.all() });
    },
  });

  return { addProduct, updateProduct, deleteProduct };
}
