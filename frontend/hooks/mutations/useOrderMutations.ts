/**
 * Order Mutation Hooks
 *
 * Generated via the mutation factory for standard CRUD operations
 * on order resources with automatic cache invalidation.
 */

import { createMutationHooks } from './mutationFactory';
import salesService from '@/services/api/salesService';

export const {
  useCreate: useCreateOrder,
  useUpdate: useUpdateOrder,
  useDelete: useDeleteOrder,
} = createMutationHooks({
  resource: 'orders',
  createFn: salesService.createOrder,
  updateFn: salesService.updateOrder,
  deleteFn: (id: string) => salesService.deleteOrder(id).then(() => {}),
});
