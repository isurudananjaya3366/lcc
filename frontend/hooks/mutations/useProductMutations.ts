/**
 * Product Mutation Hooks
 *
 * Create / Update / Delete mutations for products with
 * optimistic updates, proper cache invalidation, and
 * rollback on error.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { QueryClient, QueryKey } from '@tanstack/react-query';
import productService from '@/services/api/productService';
import { productKeys } from '@/lib/queryKeys';
import { invalidateCache, removeFromCache, getRelatedResources } from './cacheInvalidation';
import type { Product, ProductCreateRequest, ProductUpdateRequest } from '@/types/product';
import type { APIResponse, PaginatedResponse } from '@/types/api';

// ── Create ─────────────────────────────────────────────────────

export function useCreateProduct() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: ProductCreateRequest) => productService.createProduct(input),
    onSuccess: () => {
      invalidateCache(queryClient, {
        resource: 'products',
        strategy: 'PARTIAL',
        relatedResources: getRelatedResources('products', 'create'),
      });
    },
    retry: false,
  });
}

// ── Update (with optimistic update) ────────────────────────────

interface UpdateContext {
  previousProduct: APIResponse<Product> | undefined;
  previousLists: [QueryKey, PaginatedResponse<Product> | undefined][];
}

export function useUpdateProduct() {
  const queryClient = useQueryClient();

  return useMutation<
    APIResponse<Product>,
    Error,
    { id: string; updates: ProductUpdateRequest },
    UpdateContext
  >({
    mutationFn: ({ id, updates }) => productService.updateProduct(id, updates),

    onMutate: async ({ id, updates }) => {
      // Cancel in-flight queries so they don't overwrite optimistic data
      await queryClient.cancelQueries({ queryKey: productKeys.detail(id) });
      await queryClient.cancelQueries({ queryKey: productKeys.lists() });

      // Snapshot current detail
      const previousProduct = queryClient.getQueryData<APIResponse<Product>>(
        productKeys.detail(id)
      );

      // Snapshot list queries
      const previousLists: UpdateContext['previousLists'] = [];
      queryClient
        .getQueriesData<PaginatedResponse<Product>>({
          queryKey: productKeys.lists(),
        })
        .forEach(([key, data]) => {
          previousLists.push([key, data]);
        });

      // Optimistic update on detail
      if (previousProduct) {
        queryClient.setQueryData<APIResponse<Product>>(productKeys.detail(id), {
          ...previousProduct,
          data: { ...previousProduct.data, ...updates } as Product,
        });
      }

      // Optimistic update on lists
      previousLists.forEach(([key, listData]) => {
        if (!listData) return;
        queryClient.setQueryData<PaginatedResponse<Product>>(key, {
          ...listData,
          data: listData.data.map((item) => {
            const productItem = item as Product & { id: string };
            return productItem.id === id ? { ...productItem, ...updates } : item;
          }) as Product[],
        });
      });

      return { previousProduct, previousLists };
    },

    onError: (_error, { id }, context) => {
      // Rollback on failure
      if (context?.previousProduct) {
        queryClient.setQueryData(productKeys.detail(id), context.previousProduct);
      }
      context?.previousLists.forEach(([key, data]) => {
        queryClient.setQueryData(key, data);
      });
    },

    onSettled: (_data, _error, { id }) => {
      // Always re-fetch to ensure consistency
      queryClient.invalidateQueries({ queryKey: productKeys.detail(id) });
      invalidateCache(queryClient, {
        resource: 'products',
        strategy: 'PARTIAL',
        relatedResources: getRelatedResources('products', 'update'),
      });
    },

    retry: false,
  });
}

// ── Delete ─────────────────────────────────────────────────────

export function useDeleteProduct() {
  const queryClient = useQueryClient();

  return useMutation<APIResponse<void>, Error, string>({
    mutationFn: (id: string) => productService.deleteProduct(id),

    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: productKeys.all() });
    },

    onSuccess: (_data, id) => {
      removeFromCache(queryClient, 'products', id);
      invalidateCache(queryClient, {
        resource: 'products',
        strategy: 'PARTIAL',
        relatedResources: getRelatedResources('products', 'delete'),
      });
    },

    retry: false,
  });
}
