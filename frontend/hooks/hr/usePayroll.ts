'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import payrollService from '@/services/api/payrollService';

const payrollKeys = {
  all: () => ['payroll'] as const,
  runs: (filters?: PayrollFilters) => ['payroll', 'runs', filters] as const,
  detail: (id: string) => ['payroll', 'detail', id] as const,
  items: (payrollId: string) => ['payroll', 'items', payrollId] as const,
  payslips: (employeeId: string, year?: number) =>
    ['payroll', 'payslips', employeeId, year] as const,
};

export interface PayrollFilters {
  month?: number;
  year?: number;
  status?: string;
}

export function usePayrollRuns(filters?: PayrollFilters) {
  return useQuery({
    queryKey: payrollKeys.runs(filters),
    queryFn: () => payrollService.getPayrollRuns(filters),
    staleTime: 5 * 60 * 1000,
    placeholderData: (prev) => prev,
  });
}

export function usePayrollById(id: string) {
  return useQuery({
    queryKey: payrollKeys.detail(id),
    queryFn: () => payrollService.getPayrollById(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function usePayrollItems(payrollId: string) {
  return useQuery({
    queryKey: payrollKeys.items(payrollId),
    queryFn: () => payrollService.getPayrollItems(payrollId),
    enabled: !!payrollId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useEmployeePayslips(employeeId: string, year?: number) {
  return useQuery({
    queryKey: payrollKeys.payslips(employeeId, year),
    queryFn: () => payrollService.getEmployeePayslips(employeeId, { year }),
    enabled: !!employeeId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCreatePayrollRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { month: number; year: number; description?: string }) =>
      payrollService.createPayrollRun(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.all() });
    },
  });
}

export function useProcessPayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => payrollService.processPayroll(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.all() });
    },
  });
}

export function useApprovePayroll() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => payrollService.approvePayroll(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: payrollKeys.all() });
    },
  });
}

export function useDownloadPayslipPdf() {
  return useMutation({
    mutationFn: ({ payrollId, employeeId }: { payrollId: string; employeeId: string }) =>
      payrollService.downloadPayslipPdf(payrollId, employeeId),
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'payslip.pdf';
      a.click();
      URL.revokeObjectURL(url);
    },
  });
}
