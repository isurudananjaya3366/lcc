/**
 * useInvoices — fetch paginated invoice list
 */

import { useQuery } from '@tanstack/react-query';
import { salesKeys } from '@/lib/queryKeys';
import { invoiceService } from '@/services/api';

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
    queryFn: () => invoiceService.getInvoices(filters),
    staleTime: 1 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
