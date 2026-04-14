'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown, ArrowDown, ArrowUp, Edit, ArrowRightLeft, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { StockMovement, StockMovementType } from '@/types/inventory';

const typeBadge: Record<
  StockMovementType,
  { label: string; class: string; icon: React.ComponentType<{ className?: string }> }
> = {
  PURCHASE: {
    label: 'Purchase',
    class: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    icon: ArrowDown,
  },
  SALE: {
    label: 'Sale',
    class: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    icon: ArrowUp,
  },
  ADJUSTMENT: {
    label: 'Adjustment',
    class: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    icon: Edit,
  },
  TRANSFER: {
    label: 'Transfer',
    class: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    icon: ArrowRightLeft,
  },
  RETURN: {
    label: 'Return',
    class: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    icon: RotateCcw,
  },
  DAMAGE: {
    label: 'Damage',
    class: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    icon: Edit,
  },
};

export function getMovementColumns(): ColumnDef<StockMovement>[] {
  return [
    {
      accessorKey: 'createdAt',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Date/Time
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const date = new Date(row.original.createdAt);
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
        <div>
          <div className="font-medium text-gray-900 dark:text-gray-100">
            {row.original.productId}
          </div>
          <div className="text-xs font-mono text-gray-500">{row.original.sku}</div>
        </div>
      ),
      size: 200,
    },
    {
      accessorKey: 'movementType',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Type
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const config = typeBadge[row.original.movementType] ?? typeBadge.ADJUSTMENT;
        const Icon = config.icon;
        return (
          <span
            className={cn(
              'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
              config.class
            )}
          >
            <Icon className="h-3 w-3" />
            {config.label}
          </span>
        );
      },
      size: 120,
    },
    {
      accessorKey: 'quantity',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Quantity
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const isPositive =
          row.original.movementType === 'PURCHASE' || row.original.movementType === 'RETURN';
        return (
          <span
            className={cn(
              'font-semibold',
              isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
            )}
          >
            {isPositive ? '+' : '-'}
            {Math.abs(row.original.quantity)}
          </span>
        );
      },
      size: 100,
    },
    {
      id: 'location',
      header: 'From / To',
      cell: ({ row }) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {row.original.sourceWarehouseId ?? '—'} → {row.original.destinationWarehouseId ?? '—'}
        </span>
      ),
      enableSorting: false,
      size: 150,
    },
    {
      id: 'reference',
      header: 'Reference',
      cell: ({ row }) => (
        <span className="font-mono text-xs text-gray-500 dark:text-gray-400">
          {row.original.referenceId ?? '—'}
        </span>
      ),
      enableSorting: false,
      size: 150,
    },
    {
      accessorKey: 'createdBy',
      header: 'User',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">{row.original.createdBy}</span>
      ),
      enableSorting: false,
      size: 120,
    },
  ];
}
