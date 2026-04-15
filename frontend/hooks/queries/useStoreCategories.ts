'use client';

import { useQuery } from '@tanstack/react-query';
import { storeQueryKeys, type StoreProductFilters } from '@/lib/storeQueryKeys';
import { useState, useEffect } from 'react';
import {
  getCategories,
  getCategoriesTree,
  getCategory,
  getCategoryProducts,
  getCategoryBreadcrumb,
  getSubcategories,
  type Category,
  type CategoryTree,
} from '@/lib/api/store/modules/categories';
import { getStoreClient } from '@/lib/api/store/client';

// ─── useCategories ──────────────────────────────────────────────────────────

export function useCategories() {
  return useQuery({
    queryKey: storeQueryKeys.categories.all(),
    queryFn: () => getCategories(),
    staleTime: 15 * 60 * 1000,
  });
}

// ─── useCategory ────────────────────────────────────────────────────────────

export function useCategory(slug: string, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: storeQueryKeys.categories.detail(slug),
    queryFn: () => getCategory(slug),
    enabled: options?.enabled ?? !!slug,
    staleTime: 15 * 60 * 1000,
  });
}

// ─── useCategoryTree ────────────────────────────────────────────────────────

export function useCategoryTree() {
  return useQuery({
    queryKey: storeQueryKeys.categories.tree(),
    queryFn: () => getCategoriesTree(),
    staleTime: 20 * 60 * 1000,
  });
}

// ─── useCategoryProducts ────────────────────────────────────────────────────

export function useCategoryProducts(slug: string, filters?: StoreProductFilters) {
  return useQuery({
    queryKey: storeQueryKeys.categories.products(slug, filters),
    queryFn: () =>
      getCategoryProducts(slug, {
        page: filters?.page,
        page_size: filters?.limit,
        sort: filters?.sort,
      }),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000,
  });
}

// ─── useCategoryBreadcrumb ──────────────────────────────────────────────────

export function useCategoryBreadcrumb(categoryId: number) {
  return useQuery({
    queryKey: storeQueryKeys.categories.breadcrumb(categoryId),
    queryFn: () => getCategoryBreadcrumb(categoryId),
    enabled: !!categoryId,
    staleTime: 15 * 60 * 1000,
  });
}

// ─── useFeaturedCategories ──────────────────────────────────────────────────

export function useFeaturedCategories() {
  return useQuery({
    queryKey: storeQueryKeys.categories.featured(),
    queryFn: () => getCategories({ ordering: '-product_count' }),
    staleTime: 15 * 60 * 1000,
  });
}

// ─── Utility Functions ──────────────────────────────────────────────────────

interface FlatNode extends Category {
  depth: number;
  hasChildren: boolean;
}

export function flattenCategoryTree(tree: CategoryTree[], depth: number = 0): FlatNode[] {
  const result: FlatNode[] = [];
  for (const node of tree) {
    result.push({
      ...node,
      depth,
      hasChildren: node.children.length > 0,
    });
    if (node.children.length > 0) {
      result.push(...flattenCategoryTree(node.children, depth + 1));
    }
  }
  return result;
}

export function findCategoryById(tree: CategoryTree[], id: number): CategoryTree | null {
  for (const node of tree) {
    if (node.id === id) return node;
    if (node.children.length > 0) {
      const found = findCategoryById(node.children, id);
      if (found) return found;
    }
  }
  return null;
}

// ─── useCategoryFilters ─────────────────────────────────────────────────────

export interface CategoryFilterOptions {
  priceRange: { min: number; max: number };
  attributes: Record<string, string[]>;
  brands: string[];
}

export function useCategoryFilters(slug: string) {
  return useQuery({
    queryKey: storeQueryKeys.categories.filters(slug),
    queryFn: async (): Promise<CategoryFilterOptions> => {
      const { data } = await getStoreClient().get(`/categories/${slug}/filters/`);
      return data;
    },
    enabled: !!slug,
    staleTime: 10 * 60 * 1000, // 10 minutes — filters don't change often
  });
}

// ─── useCategorySearch ──────────────────────────────────────────────────────

export function useCategorySearch(slug: string, query: string, debounceMs = 300) {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), debounceMs);
    return () => clearTimeout(timer);
  }, [query, debounceMs]);

  return useQuery({
    queryKey: [...storeQueryKeys.categories.products(slug), 'search', debouncedQuery] as const,
    queryFn: () =>
      getStoreClient()
        .get(`/categories/${slug}/products/`, { params: { search: debouncedQuery } })
        .then((r) => r.data),
    enabled: !!slug && debouncedQuery.length >= 2,
    staleTime: 1 * 60 * 1000,
  });
}
