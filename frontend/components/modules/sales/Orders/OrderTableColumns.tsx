'use client';

import { type ColumnDef } from '@tanstack/react-table';
import Link from 'next/link';
import { ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type { Order, PaymentStatus } from '@/types/sales';
import { OrderStatusBadge } from './cells/OrderStatusBadge';
import { OrderActionsCell } from './cells/OrderActionsCell';

const paymentStatusColors: Record<PaymentStatus, string> = {
  UNPAID: 'bg-red-100 text-red-800',
  PARTIAL: 'bg-yellow-100 text-yellow-800',
  PAID: 'bg-green-100 text-green-800',
  OVERPAID: 'bg-blue-100 text-blue-800',
  REFUNDED: 'bg-orange-100 text-orange-800',
};

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export const orderTableColumns: ColumnDef<Order>[] = [
  {
    accessorKey: 'orderNumber',
    header: ({ column }) => (
      <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
        Order #
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <Link
        href={`/orders/${row.original.id}`}
        className="font-medium text-blue-600 hover:underline dark:text-blue-400"
      >
        {row.getValue('orderNumber')}
      </Link>
    ),
  },
  {
    accessorKey: 'customerName',
    header: 'Customer',
    cell: ({ row }) => (
      <span className="text-sm">{row.getValue('customerName') || 'Walk-in Customer'}</span>
    ),
  },
  {
    accessorKey: 'orderDate',
    header: ({ column }) => (
      <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
        Date
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => {
      const date = new Date(row.getValue('orderDate'));
      return <span className="text-sm">{date.toLocaleDateString()}</span>;
    },
  },
  {
    accessorKey: 'total',
    header: ({ column }) => (
      <Button variant="ghost" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
        Total
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => <span className="font-medium">{formatCurrency(row.getValue('total'))}</span>,
  },
  {
    id: 'itemsCount',
    header: 'Items',
    cell: ({ row }) => (
      <span className="text-center text-sm">{row.original.items?.length ?? 0}</span>
    ),
    enableSorting: false,
  },
  {
    accessorKey: 'orderStatus',
    header: 'Status',
    cell: ({ row }) => <OrderStatusBadge status={row.original.orderStatus} />,
  },
  {
    accessorKey: 'paymentStatus',
    header: 'Payment',
    cell: ({ row }) => {
      const status = row.getValue('paymentStatus') as PaymentStatus;
      return (
        <Badge className={paymentStatusColors[status]} variant="secondary">
          {status.replace(/_/g, ' ')}
        </Badge>
      );
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => <OrderActionsCell order={row.original} />,
  },
];
