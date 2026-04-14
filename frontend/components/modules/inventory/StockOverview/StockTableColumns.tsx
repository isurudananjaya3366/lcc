'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { StockLevel } from '@/types/inventory';
import { StockLevelCell } from './cells/StockLevelCell';
import { StockActionsCell } from './cells/StockActionsCell';

export function getStockColumns(): ColumnDef<StockLevel>[] {
  return [
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
      size: 250,
    },
    {
      id: 'sku',
      accessorKey: 'variantId',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          SKU
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <span className="font-mono text-sm text-gray-600 dark:text-gray-400">
          {row.original.variantId ?? '—'}
        </span>
      ),
      size: 120,
    },
    {
      accessorKey: 'warehouseId',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Warehouse
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">{row.original.warehouseId}</span>
      ),
      size: 150,
    },
    {
      accessorKey: 'quantityAvailable',
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Available
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <span className="font-semibold text-gray-900 dark:text-gray-100">
          {row.original.quantityAvailable.toLocaleString()}
        </span>
      ),
      size: 100,
    },
    {
      accessorKey: 'quantityReserved',
      header: 'Reserved',
      cell: ({ row }) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {row.original.quantityReserved.toLocaleString()}
        </span>
      ),
      enableSorting: false,
      size: 100,
    },
    {
      id: 'reorderPoint',
      header: 'Reorder Point',
      cell: ({ row }) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {row.original.quantityOnOrder > 0 ? row.original.quantityOnOrder.toLocaleString() : '—'}
        </span>
      ),
      enableSorting: false,
      size: 100,
    },
    {
      id: 'status',
      header: 'Status',
      cell: ({ row }) => (
        <StockLevelCell
          quantity={row.original.quantityAvailable}
          reorderPoint={row.original.quantityOnOrder}
        />
      ),
      enableSorting: false,
      size: 120,
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => (
        <StockActionsCell
          productId={row.original.productId}
          warehouseId={row.original.warehouseId}
        />
      ),
      enableSorting: false,
      enableHiding: false,
      size: 80,
    },
  ];
}
