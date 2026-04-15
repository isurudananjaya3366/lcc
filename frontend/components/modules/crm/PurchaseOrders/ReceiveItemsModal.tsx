'use client';

import { useState } from 'react';
import { Package } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { useReceivePurchaseOrder } from '@/hooks/crm/usePurchaseOrders';
import type { PurchaseOrder } from '@/types/vendor';

interface ReceiveItemsModalProps {
  po: PurchaseOrder;
}

export function ReceiveItemsModal({ po }: ReceiveItemsModalProps) {
  const [open, setOpen] = useState(false);
  const receivePO = useReceivePurchaseOrder();

  const [quantities, setQuantities] = useState<Record<number, number>>(() => {
    const initial: Record<number, number> = {};
    po.items.forEach((_, idx) => {
      initial[idx] = 0;
    });
    return initial;
  });

  const hasItemsToReceive = Object.values(quantities).some((q) => q > 0);

  function handleQuantityChange(index: number, value: string) {
    const num = parseInt(value, 10);
    if (isNaN(num) || num < 0) return;
    const item = po.items[index];
    if (!item) return;
    const max = item.quantity;
    setQuantities((prev) => ({ ...prev, [index]: Math.min(num, max) }));
  }

  function handleReceiveAll() {
    const updated: Record<number, number> = {};
    po.items.forEach((item, idx) => {
      updated[idx] = item.quantity;
    });
    setQuantities(updated);
  }

  function handleSubmit() {
    const receivedItems = po.items
      .map((item, idx) => ({
        itemId: item.productId,
        quantityReceived: quantities[idx] ?? 0,
      }))
      .filter((ri) => ri.quantityReceived > 0);

    if (receivedItems.length === 0) return;

    receivePO.mutate(
      { id: po.id, receivedItems },
      {
        onSuccess: () => {
          setOpen(false);
        },
      }
    );
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm">
          <Package className="mr-2 h-4 w-4" />
          Receive Items
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Receive Items — PO #{po.poNumber}</DialogTitle>
          <DialogDescription>
            Enter the quantity received for each item. Items will be added to inventory.
          </DialogDescription>
        </DialogHeader>

        <div className="max-h-[400px] overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead className="text-right">Ordered</TableHead>
                <TableHead className="text-right">Unit Cost</TableHead>
                <TableHead className="text-right w-32">Qty to Receive</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {po.items.map((item, idx) => (
                <TableRow key={idx}>
                  <TableCell className="font-medium">{item.productId}</TableCell>
                  <TableCell className="text-right">{item.quantity}</TableCell>
                  <TableCell className="text-right">
                    ₨ {item.unitCost.toLocaleString('en-LK')}
                  </TableCell>
                  <TableCell className="text-right">
                    <Input
                      type="number"
                      min={0}
                      max={item.quantity}
                      value={quantities[idx] ?? 0}
                      onChange={(e) => handleQuantityChange(idx, e.target.value)}
                      className="w-24 ml-auto text-right"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <DialogFooter className="flex items-center justify-between sm:justify-between">
          <Button type="button" variant="outline" size="sm" onClick={handleReceiveAll}>
            Receive All
          </Button>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={!hasItemsToReceive || receivePO.isPending}>
              {receivePO.isPending ? 'Receiving...' : 'Confirm Receipt'}
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
