/**
 * Customer Mutation Hooks
 *
 * Generated via the mutation factory for standard CRUD operations
 * on customer resources with automatic cache invalidation.
 */

import { createMutationHooks } from './mutationFactory';
import customerService from '@/services/api/customerService';

export const {
  useCreate: useCreateCustomer,
  useUpdate: useUpdateCustomer,
  useDelete: useDeleteCustomer,
} = createMutationHooks({
  resource: 'customers',
  createFn: customerService.createCustomer,
  updateFn: customerService.updateCustomer,
  deleteFn: async (id: string) => {
    await customerService.deleteCustomer(id);
  },
});
