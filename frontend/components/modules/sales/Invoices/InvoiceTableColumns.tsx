'use client';

import { createColumnHelper } from '@tanstack/react-table';
import Link from 'next/link';
import { InvoiceStatusBadge } from './InvoiceStatusBadge';
import { InvoiceActionsCell } from './InvoiceActionsCell';
import type { Invoice } from '@/services/api/invoiceService';

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

const columnHelper = createColumnHelper<Invoice>();

export interface InvoiceColumnCallbacks {
  onSend?: (invoice: Invoice) => void;
  onVoid?: (invoice: Invoice) => void;
  onDownload?: (invoice: Invoice) => void;
}

export function getInvoiceColumns(callbacks?: InvoiceColumnCallbacks) {
  return [
    columnHelper.accessor('invoiceNumber', {
      header: 'Invoice #',
      size: 120,
      cell: (info) => (
        <Link
          href={`/invoices/${info.row.original.id}`}
          className="font-medium text-blue-600 hover:underline dark:text-blue-400"
        >
          {info.getValue()}
        </Link>
      ),
    }),
    columnHelper.accessor('customerName', {
      header: 'Customer',
      size: 200,
      cell: (info) => <span className="truncate block max-w-[200px]">{info.getValue()}</span>,
    }),
    columnHelper.accessor('issueDate', {
      header: 'Date',
      size: 120,
      cell: (info) => formatDate(info.getValue()),
    }),
    columnHelper.accessor('dueDate', {
      header: 'Due Date',
      size: 120,
      cell: (info) => {
        const dueDate = new Date(info.getValue());
        const isOverdue = dueDate < new Date() && info.row.original.balanceDue > 0;
        return (
          <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
            {formatDate(info.getValue())}
          </span>
        );
      },
    }),
    columnHelper.accessor('total', {
      header: () => <span className="text-right block">Amount (LKR)</span>,
      size: 120,
      cell: (info) => (
        <span className="text-right block font-medium">{formatCurrency(info.getValue())}</span>
      ),
    }),
    columnHelper.accessor('status', {
      header: 'Status',
      size: 100,
      cell: (info) => <InvoiceStatusBadge status={info.getValue()} />,
    }),
    columnHelper.display({
      id: 'actions',
      size: 80,
      cell: (info) => (
        <InvoiceActionsCell
          invoice={info.row.original}
          onSend={callbacks?.onSend}
          onVoid={callbacks?.onVoid}
          onDownload={callbacks?.onDownload}
        />
      ),
    }),
  ];
}
