'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { StockTransfer, StockMovementStatus } from '@/types/inventory';
import { TransferStatusBadge } from './TransferStatusBadge';

export function getTransferColumns(): ColumnDef<StockTransfer>[] {
  return [
    {
      accessorKey: 'requestDate',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Date
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const date = new Date(row.original.requestDate);
        return (
          <div>
            <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {date.toLocaleDateString('en-US', {
                month: 'short',
                day: '2-digit',
                year: 'numeric',
              })}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </div>
          </div>
        );
      },
      size: 150,
    },
    {
      accessorKey: 'transferNumber',
      header: 'Reference',
      cell: ({ row }) => (
        <span className="font-mono text-sm font-medium text-blue-600 dark:text-blue-400">
          {row.original.transferNumber}
        </span>
      ),
      size: 140,
    },
    {
      accessorKey: 'sourceWarehouseId',
      header: 'From',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {row.original.sourceWarehouseId}
        </span>
      ),
      enableSorting: false,
      size: 150,
    },
    {
      accessorKey: 'destinationWarehouseId',
      header: 'To',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {row.original.destinationWarehouseId}
        </span>
      ),
      enableSorting: false,
      size: 150,
    },
    {
      id: 'itemCount',
      header: 'Items',
      cell: ({ row }) => {
        const itemCount = row.original.items.length;
        const totalQty = row.original.items.reduce((sum, item) => sum + item.quantity, 0);
        return (
          <div className="text-sm">
            <span className="font-medium text-gray-900 dark:text-gray-100">{itemCount}</span>
            <span className="ml-1 text-gray-500 dark:text-gray-400">({totalQty} units)</span>
          </div>
        );
      },
      enableSorting: false,
      size: 120,
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <TransferStatusBadge status={row.original.status} />,
      enableSorting: false,
      size: 120,
    },
    {
      accessorKey: 'requestedBy',
      header: 'Requested By',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">{row.original.requestedBy}</span>
      ),
      enableSorting: false,
      size: 120,
    },
  ];
}
