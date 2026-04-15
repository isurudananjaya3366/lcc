'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { purchaseOrderKeys, type POFilters } from '@/lib/queryKeys';
import vendorService from '@/services/api/vendorService';
import type { PurchaseOrder } from '@/types/vendor';

export function usePurchaseOrders(filters?: POFilters) {
  return useQuery({
    queryKey: purchaseOrderKeys.list(filters),
    queryFn: () =>
      vendorService.getPurchaseOrders({
        vendorId: filters?.vendorId,
        status: filters?.status,
        startDate: filters?.startDate,
        endDate: filters?.endDate,
      }),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function usePurchaseOrder(id: string) {
  return useQuery({
    queryKey: purchaseOrderKeys.detail(id),
    queryFn: () => vendorService.getPurchaseOrderById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreatePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Omit<PurchaseOrder, 'id' | 'poNumber' | 'createdAt'>) =>
      vendorService.createPurchaseOrder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.lists() });
    },
  });
}

export function useUpdatePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<PurchaseOrder> }) =>
      vendorService.updatePurchaseOrder(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: purchaseOrderKeys.detail(variables.id),
      });
    },
  });
}

export function useCancelPurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      vendorService.cancelPurchaseOrder(id, reason),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: purchaseOrderKeys.detail(variables.id),
      });
    },
  });
}

export function useReceivePurchaseOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      receivedItems,
    }: {
      id: string;
      receivedItems: { itemId: string; quantityReceived: number }[];
    }) => vendorService.receivePurchaseOrder(id, receivedItems),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: purchaseOrderKeys.lists() });
      queryClient.invalidateQueries({
        queryKey: purchaseOrderKeys.detail(variables.id),
      });
    },
  });
}
