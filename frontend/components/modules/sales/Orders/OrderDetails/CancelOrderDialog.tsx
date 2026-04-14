'use client';

import { useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
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
    <AlertDialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Cancel Order {order.orderNumber}?</AlertDialogTitle>
          <AlertDialogDescription>
            This action cannot be undone. The order will be marked as cancelled and the customer
            will be notified.
          </AlertDialogDescription>
        </AlertDialogHeader>

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

        <AlertDialogFooter>
          <AlertDialogCancel disabled={isSubmitting}>Keep Order</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isSubmitting}
            className="bg-red-600 hover:bg-red-700"
          >
            {isSubmitting ? 'Cancelling...' : 'Cancel Order'}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
