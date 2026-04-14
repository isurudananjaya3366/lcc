// Mutation hooks
export { useCreateProduct, useUpdateProduct, useDeleteProduct } from './useProductMutations';
export { useCreateCustomer, useUpdateCustomer, useDeleteCustomer } from './useCustomerMutations';
export { useCreateOrder, useUpdateOrder, useDeleteOrder } from './useOrderMutations';

// Cache invalidation utilities
export { invalidateCache, removeFromCache, getRelatedResources } from './cacheInvalidation';
export type { InvalidationStrategy, InvalidationConfig } from './cacheInvalidation';

// Mutation factory
export { createMutationHooks, optimisticUpdateHelper } from './mutationFactory';

// Prefetch utilities
export { usePrefetch, usePrefetchOnHover, usePrefetchOnFocus } from './usePrefetch';
