'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import type { Order } from '@/types/sales';

interface CancelOrderDialogProps {
  isOpen: boolean;
  onClose: () => void;
  order: Order;
  onConfirm: (reason: string) => Promise<void>;
}

export function CancelOrderDialog({ isOpen, onClose, order, onConfirm }: CancelOrderDialogProps) {
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleConfirm = async () => {
    setIsSubmitting(true);
    try {
      await onConfirm(reason);
      setReason('');
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Cancel Order {order.orderNumber}?</DialogTitle>
          <DialogDescription>
            This action cannot be undone. The order will be marked as cancelled and the customer
            will be notified.
          </DialogDescription>
        </DialogHeader>

        <div className="py-2">
          <Label htmlFor="cancelReason">Reason for cancellation</Label>
          <Textarea
            id="cancelReason"
            placeholder="Enter the reason for cancellation..."
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            className="mt-1"
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={isSubmitting}>
            Keep Order
          </Button>
          <Button variant="destructive" onClick={handleConfirm} disabled={isSubmitting}>
            {isSubmitting ? 'Cancelling...' : 'Cancel Order'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
