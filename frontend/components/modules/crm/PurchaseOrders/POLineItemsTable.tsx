'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  TableFooter,
} from '@/components/ui/table';
import type { PurchaseOrder } from '@/types/vendor';

interface POLineItemsTableProps {
  po: PurchaseOrder;
}

export function POLineItemsTable({ po }: POLineItemsTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[60px]">#</TableHead>
            <TableHead>Product ID</TableHead>
            <TableHead className="text-right">Qty</TableHead>
            <TableHead className="text-right">Unit Cost</TableHead>
            <TableHead className="text-right">Total</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {po.items.map((item, idx) => (
            <TableRow key={`${item.productId}-${idx}`}>
              <TableCell className="text-muted-foreground">{idx + 1}</TableCell>
              <TableCell className="font-medium">{item.productId}</TableCell>
              <TableCell className="text-right">{item.quantity}</TableCell>
              <TableCell className="text-right">
                ₨ {item.unitCost.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
              </TableCell>
              <TableCell className="text-right">
                ₨ {item.total.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell colSpan={4} className="text-right font-medium">
              Subtotal
            </TableCell>
            <TableCell className="text-right">
              ₨ {po.subtotal.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell colSpan={4} className="text-right font-medium">
              Tax
            </TableCell>
            <TableCell className="text-right">
              ₨ {po.tax.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell colSpan={4} className="text-right font-medium">
              Shipping
            </TableCell>
            <TableCell className="text-right">
              ₨ {po.shipping.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell colSpan={4} className="text-right text-base font-bold">
              Total
            </TableCell>
            <TableCell className="text-right text-base font-bold">
              ₨ {po.total.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
            </TableCell>
          </TableRow>
        </TableFooter>
      </Table>
    </div>
  );
}
