'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customerKeys } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';
import type {
  CustomerSearchParams,
  CustomerCreateRequest,
  CustomerUpdateRequest,
} from '@/types/customer';

export function useCustomers(params?: CustomerSearchParams) {
  return useQuery({
    queryKey: customerKeys.list(params),
    queryFn: () => customerService.getCustomers(params),
  });
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: customerKeys.detail(id),
    queryFn: () => customerService.getCustomerById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    refetchOnWindowFocus: true,
    retry: 2,
  });
}

export function useUpdateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: CustomerUpdateRequest }) =>
      customerService.updateCustomer(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: customerKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
}

export function useCreateCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CustomerCreateRequest) => customerService.createCustomer(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
}

export function useDeleteCustomer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => customerService.deleteCustomer(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: customerKeys.lists() });
    },
  });
}

export function useAdjustCredit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<{ creditLimit: number }> }) =>
      customerService.updateCustomerCredit(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: customerKeys.detail(variables.id) });
    },
  });
}
