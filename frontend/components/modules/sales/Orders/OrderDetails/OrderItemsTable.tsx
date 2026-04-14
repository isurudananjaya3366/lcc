'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { OrderItem } from '@/types/sales';

interface OrderItemsTableProps {
  items: OrderItem[];
  editable?: boolean;
  isLoading?: boolean;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

export function OrderItemsTable({ items, editable, isLoading }: OrderItemsTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-3 pt-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-12 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Order Items</CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="py-6 text-center text-sm text-gray-500">No items in this order</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[40%]">Product</TableHead>
                <TableHead>SKU</TableHead>
                <TableHead className="text-center">Qty</TableHead>
                <TableHead className="text-right">Unit Price</TableHead>
                <TableHead className="text-right">Discount</TableHead>
                <TableHead className="text-right">Tax</TableHead>
                <TableHead className="text-right">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id} className="group">
                  <TableCell>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100">{item.name}</p>
                      {item.description && (
                        <p className="text-xs text-gray-500 line-clamp-1">{item.description}</p>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-gray-500 font-mono">{item.sku}</TableCell>
                  <TableCell className="text-center font-mono">{item.quantity}</TableCell>
                  <TableCell className="text-right">{formatCurrency(item.unitPrice)}</TableCell>
                  <TableCell className="text-right">
                    {item.discount > 0
                      ? item.discountType === 'PERCENTAGE'
                        ? `${item.discount}%`
                        : formatCurrency(item.discount)
                      : '—'}
                  </TableCell>
                  <TableCell className="text-right">{formatCurrency(item.taxAmount)}</TableCell>
                  <TableCell className="text-right font-medium">
                    {formatCurrency(item.total)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
