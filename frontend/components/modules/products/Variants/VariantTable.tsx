'use client';

import { useState } from 'react';
import type { ProductVariant } from '@/types/product';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Edit, Trash2, Copy, Clipboard } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

interface VariantTableProps {
  productId: string;
  variants: ProductVariant[];
  onEdit?: (variant: ProductVariant) => void;
  onDelete?: (variantId: string) => void;
  onBulkAction?: (action: string, ids: string[]) => void;
  isLoading?: boolean;
}

function getStockColor(quantity: number): string {
  if (quantity <= 0) return 'text-red-600 dark:text-red-400';
  if (quantity <= 10) return 'text-amber-600 dark:text-amber-400';
  return 'text-green-600 dark:text-green-400';
}

function formatLKR(value: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(value);
}

export function VariantTable({
  variants,
  onEdit,
  onDelete,
  onBulkAction,
  isLoading,
}: VariantTableProps) {
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [search, setSearch] = useState('');

  const filteredVariants = variants.filter(
    (v) =>
      v.variantName.toLowerCase().includes(search.toLowerCase()) ||
      v.sku.toLowerCase().includes(search.toLowerCase())
  );

  const allSelected =
    filteredVariants.length > 0 && filteredVariants.every((v) => selectedIds.has(v.id));

  const toggleAll = () => {
    if (allSelected) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredVariants.map((v) => v.id)));
    }
  };

  const toggleOne = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedIds(next);
  };

  const copySku = async (sku: string) => {
    await navigator.clipboard.writeText(sku);
  };

  if (isLoading) {
    return (
      <div className="space-y-3 p-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Toolbar */}
      <div className="flex items-center justify-between gap-2">
        <Input
          placeholder="Search variants..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-8 w-64"
        />
        {selectedIds.size > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">{selectedIds.size} selected</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onBulkAction?.('delete', [...selectedIds])}
              className="text-red-600 hover:text-red-700"
            >
              Delete Selected
            </Button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-md border dark:border-gray-700">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-10">
                <Checkbox checked={allSelected} onCheckedChange={toggleAll} />
              </TableHead>
              <TableHead>Variant</TableHead>
              <TableHead>SKU</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Stock</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-12" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredVariants.map((variant) => (
              <TableRow
                key={variant.id}
                className={selectedIds.has(variant.id) ? 'bg-muted/50' : ''}
              >
                <TableCell>
                  <Checkbox
                    checked={selectedIds.has(variant.id)}
                    onCheckedChange={() => toggleOne(variant.id)}
                  />
                </TableCell>
                <TableCell className="font-medium">{variant.variantName}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    <code className="text-xs">{variant.sku}</code>
                    <button
                      type="button"
                      className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      onClick={() => copySku(variant.sku)}
                      title="Copy SKU"
                    >
                      <Clipboard className="h-3 w-3" />
                    </button>
                  </div>
                </TableCell>
                <TableCell className="tabular-nums">{formatLKR(variant.price)}</TableCell>
                <TableCell>
                  <span
                    className={`tabular-nums font-medium ${getStockColor(variant.stockQuantity)}`}
                  >
                    {variant.stockQuantity}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge variant={variant.isActive ? 'default' : 'secondary'}>
                    {variant.isActive ? 'Active' : 'Inactive'}
                  </Badge>
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-7 w-7">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onEdit?.(variant)}>
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Copy className="mr-2 h-4 w-4" />
                        Duplicate
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => onDelete?.(variant.id)}
                        className="text-red-600 focus:text-red-600"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
            {filteredVariants.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={7}
                  className="py-8 text-center text-sm text-gray-500 dark:text-gray-400"
                >
                  {search
                    ? 'No variants match your search.'
                    : 'No variants created yet. Generate variants from attribute options.'}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
