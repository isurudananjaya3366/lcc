'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { StockAdjustment, AdjustmentReason } from '@/types/inventory';

const reasonLabels: Record<AdjustmentReason, string> = {
  DAMAGE: 'Damage',
  THEFT: 'Theft',
  EXPIRED: 'Expired',
  RECOUNT: 'Recount',
  ERROR: 'Error Correction',
  OTHER: 'Other',
};

export function getAdjustmentColumns(): ColumnDef<StockAdjustment>[] {
  return [
    {
      accessorKey: 'adjustedAt',
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
        const date = new Date(row.original.adjustedAt);
        return (
          <div>
            <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
              {date.toLocaleDateString()}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              {date.toLocaleTimeString()}
            </div>
          </div>
        );
      },
      size: 150,
    },
    {
      accessorKey: 'productId',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Product
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <span className="font-medium text-gray-900 dark:text-gray-100">
          {row.original.productId}
        </span>
      ),
      size: 200,
    },
    {
      accessorKey: 'warehouseId',
      header: 'Warehouse',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">{row.original.warehouseId}</span>
      ),
      enableSorting: false,
      size: 150,
    },
    {
      accessorKey: 'reason',
      header: 'Reason',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {reasonLabels[row.original.reason] ?? row.original.reason}
        </span>
      ),
      enableSorting: false,
      size: 120,
    },
    {
      accessorKey: 'difference',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Change
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const diff = row.original.difference;
        return (
          <span
            className={cn(
              'font-semibold',
              diff > 0
                ? 'text-green-600 dark:text-green-400'
                : diff < 0
                  ? 'text-red-600 dark:text-red-400'
                  : 'text-gray-500'
            )}
          >
            {diff > 0 ? '+' : ''}
            {diff}
          </span>
        );
      },
      size: 100,
    },
    {
      id: 'quantities',
      header: 'Before → After',
      cell: ({ row }) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {row.original.quantityBefore} → {row.original.quantityAfter}
        </span>
      ),
      enableSorting: false,
      size: 120,
    },
    {
      accessorKey: 'adjustedBy',
      header: 'Adjusted By',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">{row.original.adjustedBy}</span>
      ),
      enableSorting: false,
      size: 120,
    },
    {
      id: 'approval',
      header: 'Approval',
      cell: ({ row }) => {
        if (row.original.approvedBy) {
          return (
            <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/30 dark:text-green-400">
              Approved
            </span>
          );
        }
        return (
          <span className="inline-flex items-center rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400">
            Pending
          </span>
        );
      },
      enableSorting: false,
      size: 100,
    },
  ];
}
