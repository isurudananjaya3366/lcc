'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vendorKeys } from '@/lib/queryKeys';
import vendorService from '@/services/api/vendorService';
import type { VendorSearchParams, VendorCreateRequest, VendorUpdateRequest } from '@/types/vendor';

export function useVendors(params?: VendorSearchParams) {
  return useQuery({
    queryKey: vendorKeys.list(params),
    queryFn: () => vendorService.getVendors(params),
  });
}

export function useVendor(id: string) {
  return useQuery({
    queryKey: vendorKeys.detail(id),
    queryFn: () => vendorService.getVendorById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: true,
    retry: 2,
  });
}

export function useCreateVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: VendorCreateRequest) => vendorService.createVendor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: vendorKeys.lists() });
    },
  });
}

export function useUpdateVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: VendorUpdateRequest }) =>
      vendorService.updateVendor(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: vendorKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: vendorKeys.lists() });
    },
  });
}

export function useDeleteVendor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => vendorService.deleteVendor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: vendorKeys.lists() });
    },
  });
}

export function useVendorProducts(vendorId: string) {
  return useQuery({
    queryKey: vendorKeys.products(vendorId),
    queryFn: () => vendorService.getVendorProducts(vendorId),
    enabled: !!vendorId,
  });
}

export function useVendorPOs(vendorId: string) {
  return useQuery({
    queryKey: vendorKeys.purchaseOrders(vendorId),
    queryFn: () => vendorService.getPurchaseOrders({ vendorId }),
    enabled: !!vendorId,
  });
}
