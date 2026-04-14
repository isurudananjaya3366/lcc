'use client';

import type { Product } from '@/types/product';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface ProductInventoryCardProps {
  product: Product;
}

function getStockColor(quantity: number, threshold: number) {
  if (quantity <= 0) return 'text-red-600 dark:text-red-400';
  if (quantity <= threshold) return 'text-amber-600 dark:text-amber-400';
  return 'text-green-600 dark:text-green-400';
}

function getStockBadgeVariant(quantity: number, threshold: number) {
  if (quantity <= 0) return 'destructive' as const;
  if (quantity <= threshold) return 'secondary' as const;
  return 'default' as const;
}

export function ProductInventoryCard({ product }: ProductInventoryCardProps) {
  const { inventory } = product;

  if (!inventory.trackInventory) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Inventory</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Inventory tracking is disabled for this product.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Inventory</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Total Stock</p>
            <p
              className={`text-2xl font-bold tabular-nums ${getStockColor(
                inventory.stockQuantity,
                inventory.lowStockThreshold
              )}`}
            >
              {inventory.stockQuantity}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Low Stock Threshold</p>
            <p className="text-2xl font-bold tabular-nums">{inventory.lowStockThreshold}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge
            variant={getStockBadgeVariant(inventory.stockQuantity, inventory.lowStockThreshold)}
          >
            {inventory.stockQuantity <= 0
              ? 'Out of Stock'
              : inventory.stockQuantity <= inventory.lowStockThreshold
                ? 'Low Stock'
                : 'In Stock'}
          </Badge>
          {inventory.allowBackorder && <Badge variant="outline">Backorder Allowed</Badge>}
        </div>

        {inventory.warehouseAllocations && inventory.warehouseAllocations.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2">Warehouse Allocations</h4>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Warehouse</TableHead>
                  <TableHead className="text-right">Quantity</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {inventory.warehouseAllocations.map((allocation) => (
                  <TableRow key={allocation.warehouseId}>
                    <TableCell className="font-medium">{allocation.warehouseId}</TableCell>
                    <TableCell
                      className={`text-right tabular-nums ${getStockColor(
                        allocation.quantity,
                        inventory.lowStockThreshold
                      )}`}
                    >
                      {allocation.quantity}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
