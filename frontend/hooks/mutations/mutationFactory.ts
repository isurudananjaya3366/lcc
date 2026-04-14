/**
 * Generic Mutation Factory
 *
 * Creates standardised create / update / delete mutation hooks
 * for any domain resource.
 */

import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { QueryKey, UseMutationOptions } from '@tanstack/react-query';
import { invalidateCache, removeFromCache, getRelatedResources } from './cacheInvalidation';
import type { InvalidationStrategy } from './cacheInvalidation';

// ── Config ─────────────────────────────────────────────────────

interface MutationFactoryConfig {
  resource: string;
  invalidationStrategy?: InvalidationStrategy;
  optimistic?: boolean;
}

// ── Optimistic Update Helper ───────────────────────────────────

export function optimisticUpdateHelper<T>(
  queryClient: ReturnType<typeof useQueryClient>,
  resource: string,
  id: string | number,
  updates: Partial<T>
) {
  const detailKey: QueryKey = [resource, 'detail', id];
  const previous = queryClient.getQueryData<T>(detailKey);

  if (previous) {
    queryClient.setQueryData<T>(detailKey, {
      ...previous,
      ...updates,
    });
  }

  return { previous, detailKey, timestamp: Date.now() };
}

// ── Factory ────────────────────────────────────────────────────

/**
 * Creates `useCreate`, `useUpdate`, and `useDelete` mutation hooks
 * for a given resource + service.
 */
export function createMutationHooks<TData, TCreateInput, TUpdateInput>(
  config: MutationFactoryConfig & {
    createFn: (input: TCreateInput) => Promise<TData>;
    updateFn: (id: string, input: TUpdateInput) => Promise<TData>;
    deleteFn: (id: string) => Promise<void>;
  }
) {
  const { resource, invalidationStrategy = 'PARTIAL', createFn, updateFn, deleteFn } = config;

  function useCreate(options?: Omit<UseMutationOptions<TData, Error, TCreateInput>, 'mutationFn'>) {
    const queryClient = useQueryClient();
    return useMutation<TData, Error, TCreateInput>({
      mutationFn: createFn,
      onSuccess: (...args) => {
        invalidateCache(queryClient, {
          resource,
          strategy: invalidationStrategy,
          relatedResources: getRelatedResources(resource, 'create'),
        });
        options?.onSuccess?.(...args);
      },
      onError: options?.onError,
      retry: false,
    });
  }

  function useUpdate(
    options?: Omit<
      UseMutationOptions<TData, Error, { id: string; updates: TUpdateInput }>,
      'mutationFn'
    >
  ) {
    const queryClient = useQueryClient();
    return useMutation<TData, Error, { id: string; updates: TUpdateInput }>({
      mutationFn: ({ id, updates }) => updateFn(id, updates),
      onSuccess: (data, variables, ctx) => {
        invalidateCache(queryClient, {
          resource,
          id: variables.id,
          strategy: 'EXACT',
          relatedResources: getRelatedResources(resource, 'update'),
        });
        // Also invalidate list queries
        invalidateCache(queryClient, {
          resource,
          strategy: 'PARTIAL',
        });
        options?.onSuccess?.(data, variables, ctx);
      },
      onError: options?.onError,
      retry: false,
    });
  }

  function useDelete(options?: Omit<UseMutationOptions<void, Error, string>, 'mutationFn'>) {
    const queryClient = useQueryClient();
    return useMutation<void, Error, string>({
      mutationFn: deleteFn,
      onMutate: async (id) => {
        await queryClient.cancelQueries({
          queryKey: [resource] as QueryKey,
        });
        return { id };
      },
      onSuccess: (_data, id, ctx) => {
        removeFromCache(queryClient, resource, id);
        invalidateCache(queryClient, {
          resource,
          strategy: 'PARTIAL',
          relatedResources: getRelatedResources(resource, 'delete'),
        });
        options?.onSuccess?.(_data, id, ctx);
      },
      onError: options?.onError,
      retry: false,
    });
  }

  return { useCreate, useUpdate, useDelete };
}
