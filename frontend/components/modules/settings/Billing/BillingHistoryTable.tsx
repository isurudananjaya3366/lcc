'use client';

import { useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
} from '@tanstack/react-table';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { DownloadInvoice } from './DownloadInvoice';
import type { BillingInvoice } from '@/types/settings';

function formatLKR(amount: number) {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 0,
  }).format(amount);
}

function getStatusBadge(status: BillingInvoice['status']) {
  switch (status) {
    case 'PAID':
      return (
        <Badge className="bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300">
          Paid
        </Badge>
      );
    case 'PENDING':
      return (
        <Badge className="bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300">
          Pending
        </Badge>
      );
    case 'FAILED':
      return (
        <Badge className="bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300">Failed</Badge>
      );
  }
}

interface BillingHistoryTableProps {
  invoices: BillingInvoice[];
}

export function BillingHistoryTable({ invoices }: BillingHistoryTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: 'date', desc: true }]);

  const columns = useMemo<ColumnDef<BillingInvoice>[]>(
    () => [
      {
        accessorKey: 'id',
        header: 'Invoice #',
        cell: ({ row }) => (
          <span className="font-mono text-sm">INV-{row.original.id.slice(0, 3).toUpperCase()}</span>
        ),
      },
      {
        accessorKey: 'date',
        header: 'Date',
        cell: ({ row }) =>
          new Date(row.original.date).toLocaleDateString('en-LK', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          }),
      },
      {
        accessorKey: 'amount',
        header: 'Amount',
        cell: ({ row }) => formatLKR(row.original.amount),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => getStatusBadge(row.original.status),
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => (
          <DownloadInvoice
            invoiceId={row.original.id}
            invoiceNumber={`INV-${row.original.id.slice(0, 3).toUpperCase()}`}
          />
        ),
      },
    ],
    []
  );

  const table = useReactTable({
    data: invoices,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize: 10 } },
  });

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Billing History</h3>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No billing history yet.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {table.getPageCount() > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
