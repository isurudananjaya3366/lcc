'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { hrKeys } from '@/lib/queryKeys';
import type { HRFilters } from '@/lib/queryKeys';
import employeeService from '@/services/api/employeeService';
import type { EmployeeCreateRequest, EmployeeUpdateRequest } from '@/types/hr';

export function useEmployees(filters?: HRFilters) {
  return useQuery({
    queryKey: hrKeys.list(filters),
    queryFn: () =>
      employeeService.getEmployees(filters as Parameters<typeof employeeService.getEmployees>[0]),
    staleTime: 10 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: false,
  });
}

export function useEmployee(id: string) {
  return useQuery({
    queryKey: hrKeys.detail(id),
    queryFn: () => employeeService.getEmployeeById(id),
    enabled: !!id,
    staleTime: 15 * 60 * 1000,
    retry: 2,
  });
}

export function useCreateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: EmployeeCreateRequest) => employeeService.createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.lists() });
    },
  });
}

export function useUpdateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: EmployeeUpdateRequest }) =>
      employeeService.updateEmployee(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: hrKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: hrKeys.lists() });
    },
  });
}

export function useDeleteEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => employeeService.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.lists() });
    },
  });
}

export function useTerminateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { date: string; reason: string } }) =>
      employeeService.terminateEmployee(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: hrKeys.detail(variables.id) });
      queryClient.invalidateQueries({ queryKey: hrKeys.lists() });
    },
  });
}

export function useReactivateEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => employeeService.reactivateEmployee(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: hrKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: hrKeys.lists() });
    },
  });
}

export function useDepartments() {
  return useQuery({
    queryKey: ['departments'],
    queryFn: () => employeeService.getDepartments(),
    staleTime: 30 * 60 * 1000,
  });
}

export function usePositions() {
  return useQuery({
    queryKey: ['positions'],
    queryFn: () => employeeService.getPositions(),
    staleTime: 30 * 60 * 1000,
  });
}
