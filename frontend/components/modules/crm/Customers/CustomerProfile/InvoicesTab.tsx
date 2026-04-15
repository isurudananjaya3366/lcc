'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { FileText } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { customerKeys } from '@/lib/queryKeys';
import customerService from '@/services/api/customerService';

interface InvoicesTabProps {
  customerId: string;
}

interface Invoice {
  id: string;
  invoiceNumber: string;
  date: string;
  amount: number;
  dueDate: string;
  status: string;
}

function getStatusVariant(status: string) {
  switch (status.toLowerCase()) {
    case 'paid':
      return 'default';
    case 'pending':
      return 'pending';
    case 'overdue':
      return 'destructive';
    case 'partial':
      return 'processing';
    default:
      return 'outline';
  }
}

function formatLKR(amount: number): string {
  return `₨${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function getDaysUntilDue(dueDate: string): { text: string; overdue: boolean } {
  const due = new Date(dueDate);
  const now = new Date();
  const diffDays = Math.ceil((due.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return { text: `${Math.abs(diffDays)}d overdue`, overdue: true };
  if (diffDays === 0) return { text: 'Due today', overdue: false };
  return { text: `${diffDays}d remaining`, overdue: false };
}

export function InvoicesTab({ customerId }: InvoicesTabProps) {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: [...customerKeys.orders(customerId), 'invoices', { page }],
    queryFn: () => customerService.getCustomerTransactions(customerId, {}),
    enabled: !!customerId,
  });

  const invoices: Invoice[] = (data?.data ?? []).map((t) => ({
    id: t.id,
    invoiceNumber: t.referenceId ?? `INV-${t.id.slice(0, 6)}`,
    date: t.transactionDate,
    amount: t.amount,
    dueDate: t.transactionDate,
    status: t.transactionType === 'PAYMENT' ? 'Paid' : 'Pending',
  }));

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-40" />
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  if (invoices.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileText className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium">No Invoices</h3>
        <p className="text-sm text-muted-foreground">
          No invoices have been generated for this customer yet.
        </p>
      </div>
    );
  }

  const totalInvoiced = invoices.reduce((sum, inv) => sum + inv.amount, 0);
  const paidCount = invoices.filter((inv) => inv.status === 'Paid').length;
  const outstanding = invoices
    .filter((inv) => inv.status !== 'Paid')
    .reduce((sum, inv) => sum + inv.amount, 0);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">
          Invoices
          <Badge variant="secondary" className="ml-2">
            {invoices.length}
          </Badge>
        </h3>
      </div>

      <div className="grid grid-cols-3 gap-4 text-sm">
        <div>
          <p className="text-muted-foreground">Total Invoiced</p>
          <p className="font-medium">{formatLKR(totalInvoiced)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Outstanding</p>
          <p className="font-medium text-orange-600">{formatLKR(outstanding)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Paid</p>
          <p className="font-medium text-green-600">
            {paidCount} / {invoices.length}
          </p>
        </div>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Invoice #</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right">Amount</TableHead>
            <TableHead>Due Date</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {invoices.map((invoice) => {
            const dueInfo = getDaysUntilDue(invoice.dueDate);
            return (
              <TableRow
                key={invoice.id}
                className={dueInfo.overdue ? 'bg-red-50 dark:bg-red-950/20' : ''}
              >
                <TableCell>
                  <Link
                    href={`/invoices/${invoice.id}`}
                    className="text-primary hover:underline font-medium"
                  >
                    {invoice.invoiceNumber}
                  </Link>
                </TableCell>
                <TableCell className="text-sm">
                  {new Date(invoice.date).toLocaleDateString('en-LK', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </TableCell>
                <TableCell className="text-right font-medium">
                  {formatLKR(invoice.amount)}
                </TableCell>
                <TableCell>
                  <div>
                    <span className="text-sm">
                      {new Date(invoice.dueDate).toLocaleDateString('en-LK', {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                    <span
                      className={`text-xs ml-1 ${dueInfo.overdue ? 'text-red-500' : 'text-muted-foreground'}`}
                    >
                      ({dueInfo.text})
                    </span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge
                    variant={
                      getStatusVariant(invoice.status) as
                        | 'default'
                        | 'secondary'
                        | 'destructive'
                        | 'outline'
                    }
                  >
                    {invoice.status}
                  </Badge>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      {data && data.pagination && data.pagination.totalPages > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {data.pagination.totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={!data.pagination.hasNext}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

export { InvoicesTab as InvoiceHistoryTable };
