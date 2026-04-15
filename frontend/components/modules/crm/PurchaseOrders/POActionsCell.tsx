'use client';

import { useRouter } from 'next/navigation';
import { MoreHorizontal, Eye, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useState } from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useCancelPurchaseOrder } from '@/hooks/crm/usePurchaseOrders';
import type { PurchaseOrder } from '@/types/vendor';

interface POActionsCellProps {
  po: PurchaseOrder;
}

export function POActionsCell({ po }: POActionsCellProps) {
  const router = useRouter();
  const [showCancel, setShowCancel] = useState(false);
  const [reason, setReason] = useState('');
  const cancelPO = useCancelPurchaseOrder();

  const canCancel = ['DRAFT', 'SENT', 'ACKNOWLEDGED'].includes(po.status);

  function handleCancel() {
    if (!reason.trim()) return;
    cancelPO.mutate(
      { id: po.id, reason },
      {
        onSuccess: () => {
          setShowCancel(false);
          setReason('');
        },
      }
    );
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => router.push(`/purchase-orders/${po.id}`)}>
            <Eye className="mr-2 h-4 w-4" />
            View Details
          </DropdownMenuItem>
          {canCancel && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-destructive" onClick={() => setShowCancel(true)}>
                <XCircle className="mr-2 h-4 w-4" />
                Cancel PO
              </DropdownMenuItem>
            </>
          )}
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={showCancel} onOpenChange={setShowCancel}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Purchase Order</DialogTitle>
            <DialogDescription>
              Cancel PO #{po.poNumber}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="cancel-reason">Reason *</Label>
            <Textarea
              id="cancel-reason"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="Enter reason for cancellation..."
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCancel(false)}>
              Keep Order
            </Button>
            <Button
              variant="destructive"
              onClick={handleCancel}
              disabled={!reason.trim() || cancelPO.isPending}
            >
              {cancelPO.isPending ? 'Cancelling...' : 'Cancel Order'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
