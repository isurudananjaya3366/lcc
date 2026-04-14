'use client';

import { type ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import type { Product } from '@/types/product';
import { ProductNameCell } from './cells/ProductNameCell';
import { PriceCell } from './cells/PriceCell';
import { StockCell } from './cells/StockCell';
import { StatusBadgeCell } from './cells/StatusBadgeCell';
import { ActionsCell } from './cells/ActionsCell';

export function getProductColumns(options?: {
  onDelete?: (productId: string) => void;
}): ColumnDef<Product>[] {
  return [
    // Selection column
    {
      id: 'select',
      header: ({ table }) => (
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && 'indeterminate')
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
      size: 40,
    },

    // Product name column
    {
      accessorKey: 'name',
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
      cell: ({ row }) => <ProductNameCell product={row.original} />,
      size: 300,
    },

    // SKU column
    {
      accessorKey: 'sku',
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
          {row.getValue('sku')}
        </span>
      ),
      size: 120,
    },

    // Category column
    {
      id: 'category',
      accessorFn: (row) => row.categoryId,
      header: 'Category',
      cell: ({ row }) => (
        <span className="text-sm text-gray-700 dark:text-gray-300">
          {row.original.categoryId ?? '—'}
        </span>
      ),
      enableSorting: false,
      size: 150,
    },

    // Price column
    {
      id: 'price',
      accessorFn: (row) => row.pricing.basePrice,
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Price
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => <PriceCell price={row.original.pricing.basePrice} />,
      size: 120,
    },

    // Stock column
    {
      id: 'stock',
      accessorFn: (row) => row.inventory.stockQuantity,
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className="-ml-3 h-8"
        >
          Stock
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <StockCell
          quantity={row.original.inventory.stockQuantity}
          lowStockThreshold={row.original.inventory.lowStockThreshold}
        />
      ),
      size: 100,
    },

    // Status column
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }) => <StatusBadgeCell status={row.original.status} />,
      enableSorting: false,
      size: 100,
    },

    // Actions column
    {
      id: 'actions',
      header: '',
      cell: ({ row }) => <ActionsCell productId={row.original.id} onDelete={options?.onDelete} />,
      enableSorting: false,
      enableHiding: false,
      size: 60,
    },
  ];
}
