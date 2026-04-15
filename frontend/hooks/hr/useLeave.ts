'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { hrKeys } from '@/lib/queryKeys';
import leaveService from '@/services/api/leaveService';
import type { LeaveStatus } from '@/types/hr';

export interface LeaveFilters {
  employeeId?: string;
  status?: LeaveStatus;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
}

export function useLeaveRequests(filters?: LeaveFilters) {
  return useQuery({
    queryKey: [...hrKeys.leaves(), 'list', filters],
    queryFn: () => leaveService.getLeaveRequests(filters),
    staleTime: 5 * 60 * 1000,
    placeholderData: (prev) => prev,
  });
}

export function useLeaveBalance(employeeId: string) {
  return useQuery({
    queryKey: [...hrKeys.leaves(), 'balance', employeeId],
    queryFn: () => leaveService.getLeaveBalance(employeeId),
    enabled: !!employeeId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useLeaveCalendar(startDate: string, endDate: string, departmentId?: string) {
  return useQuery({
    queryKey: [...hrKeys.leaves(), 'calendar', startDate, endDate, departmentId],
    queryFn: () => leaveService.getLeaveCalendar({ startDate, endDate, departmentId }),
    staleTime: 60 * 1000,
  });
}

export function useSubmitLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      leaveType: string;
      startDate: string;
      endDate: string;
      reason?: string;
    }) => leaveService.submitLeaveRequest(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.leaves() });
    },
  });
}

export function useApproveLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, comment }: { id: string; comment?: string }) =>
      leaveService.approveLeaveRequest(id, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.leaves() });
    },
  });
}

export function useRejectLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      leaveService.rejectLeaveRequest(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.leaves() });
    },
  });
}

export function useCancelLeaveRequest() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => leaveService.cancelLeaveRequest(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.leaves() });
    },
  });
}
