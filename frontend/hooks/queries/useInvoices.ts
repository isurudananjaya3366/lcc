/**
 * useInvoices — fetch paginated invoice list
 * useInvoiceDetails — fetch single invoice
 * useSendInvoice, useVoidInvoice, useRecordPayment — mutations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { salesKeys } from '@/lib/queryKeys';
import invoiceService from '@/services/api/invoiceService';
import type { InvoiceSearchParams } from '@/services/api/invoiceService';

interface InvoiceFilters {
  search?: string;
  customerId?: string;
  status?: 'all' | 'draft' | 'sent' | 'paid' | 'overdue' | 'cancelled';
  paymentStatus?: 'all' | 'unpaid' | 'partial' | 'paid';
  startDate?: string;
  endDate?: string;
  sortBy?: 'invoiceDate' | 'dueDate' | 'totalAmount' | 'daysOverdue';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export type { InvoiceFilters };

export function useInvoices(filters?: InvoiceFilters) {
  return useQuery({
    queryKey: salesKeys.invoices(),
    queryFn: () => invoiceService.getInvoices(filters as InvoiceSearchParams | undefined),
    staleTime: 1 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}

export function useInvoiceDetails(invoiceId: string) {
  return useQuery({
    queryKey: [...salesKeys.invoices(), invoiceId],
    queryFn: () => invoiceService.getInvoiceById(invoiceId),
    select: (res) => res.data,
    enabled: !!invoiceId,
  });
}

export function useSendInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, email }: { id: string; email?: string }) =>
      invoiceService.sendInvoice(id, email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.invoices() });
    },
  });
}

export function useVoidInvoice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
      invoiceService.voidInvoice(id, reason ?? ''),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.invoices() });
    },
  });
}

export function useRecordPayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      payment,
    }: {
      id: string;
      payment: { amount: number; method: string; reference?: string; date?: string };
    }) => invoiceService.recordPayment(id, payment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: salesKeys.invoices() });
    },
  });
}
