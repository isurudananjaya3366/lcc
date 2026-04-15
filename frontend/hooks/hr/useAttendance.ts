'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { hrKeys } from '@/lib/queryKeys';
import attendanceService from '@/services/api/attendanceService';
import type { AttendanceStatus } from '@/types/hr';

export interface AttendanceFilters {
  employeeId?: string;
  departmentId?: string;
  status?: string;
  startDate: string;
  endDate: string;
  page?: number;
  limit?: number;
}

export function useAttendance(filters: AttendanceFilters) {
  return useQuery({
    queryKey: [...hrKeys.attendance(), filters],
    queryFn: () =>
      attendanceService.getAttendance(
        filters as Parameters<typeof attendanceService.getAttendance>[0]
      ),
    staleTime: 30 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}

export function useAttendanceSummary(employeeId: string, month: number, year: number) {
  return useQuery({
    queryKey: [...hrKeys.attendance(), 'summary', employeeId, month, year],
    queryFn: () => attendanceService.getAttendanceSummary({ employeeId, month, year }),
    staleTime: 60 * 1000,
  });
}

export function useDepartmentAttendance(departmentId: string, date: string) {
  return useQuery({
    queryKey: [...hrKeys.attendance(), 'department', departmentId, date],
    queryFn: () => attendanceService.getDepartmentAttendance(departmentId, date),
    enabled: !!departmentId && !!date,
    staleTime: 30 * 1000,
  });
}

export function useCheckIn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ employeeId, location }: { employeeId: string; location?: string }) =>
      attendanceService.checkIn(employeeId, location),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.attendance() });
    },
  });
}

export function useCheckOut() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ attendanceId, location }: { attendanceId: string; location?: string }) =>
      attendanceService.checkOut(attendanceId, location),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.attendance() });
    },
  });
}

export function useMarkAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      employeeId,
      date,
      status,
      notes,
    }: {
      employeeId: string;
      date: string;
      status: AttendanceStatus;
      notes?: string;
    }) => attendanceService.markAttendance(employeeId, date, status, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.attendance() });
    },
  });
}

export function useUpdateAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      updates,
    }: {
      id: string;
      updates: { status?: AttendanceStatus; notes?: string };
    }) => attendanceService.updateAttendance(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: hrKeys.attendance() });
    },
  });
}
