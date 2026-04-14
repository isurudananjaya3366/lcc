'use client';

import { useMemo } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  type SortingState,
} from '@tanstack/react-table';
import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import type { Order } from '@/types/sales';
import { orderTableColumns } from './OrderTableColumns';

interface OrdersTableProps {
  orders: Order[];
  isLoading: boolean;
}

export function OrdersTable({ orders, isLoading }: OrdersTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = useMemo(() => orderTableColumns, []);

  const table = useReactTable({
    data: orders,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: { pageSize: 25 },
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="h-10 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-12 w-full animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
        ))}
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center gap-3 text-center">
        <p className="text-lg font-medium text-gray-900 dark:text-gray-100">No orders found</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Create your first order to get started
        </p>
        <Link href="/orders/new">
          <Button>Create Order</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-4">
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
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between px-2">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Showing {table.getRowModel().rows.length} of {orders.length} orders
        </p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
