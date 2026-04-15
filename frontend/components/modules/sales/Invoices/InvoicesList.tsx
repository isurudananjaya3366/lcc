'use client';

import { useState } from 'react';
import { useInvoices } from '@/hooks/queries/useInvoices';
import type { InvoiceFilters as InvoiceFilterParams } from '@/hooks/queries/useInvoices';
import type { Invoice } from '@/services/api/invoiceService';
import { InvoiceStatus } from '@/services/api/invoiceService';
import { InvoicesHeader } from './InvoicesHeader';
import { InvoiceSummaryCards } from './InvoiceSummaryCards';
import { InvoiceFilters, type InvoiceFilterValues } from './InvoiceFilters';
import { InvoicesTable } from './InvoicesTable';

export function InvoicesList() {
  const [filters, setFilters] = useState<InvoiceFilterValues>({
    search: '',
    status: 'all',
    dateRange: 'all',
  });

  const queryFilters: InvoiceFilterParams = {
    search: filters.search || undefined,
    status:
      filters.status !== 'all' ? (filters.status as InvoiceFilterParams['status']) : undefined,
  };

  const { data, isLoading } = useInvoices(queryFilters);
  const invoices: Invoice[] = Array.isArray(data) ? data : (data?.data ?? []);

  const totalInvoices = invoices.length;
  const paidTotal = invoices
    .filter((inv: Invoice) => inv.status === InvoiceStatus.PAID)
    .reduce((sum: number, inv: Invoice) => sum + inv.total, 0);
  const outstandingTotal = invoices.reduce(
    (sum: number, inv: Invoice) => sum + (inv.balanceDue || 0),
    0
  );

  return (
    <div className="space-y-6">
      <InvoicesHeader totalCount={totalInvoices} />
      <InvoiceSummaryCards
        totalInvoices={totalInvoices}
        paidTotal={paidTotal}
        outstandingTotal={outstandingTotal}
      />
      <InvoiceFilters filters={filters} onFiltersChange={setFilters} />
      <InvoicesTable invoices={invoices} isLoading={isLoading} />
    </div>
  );
}
