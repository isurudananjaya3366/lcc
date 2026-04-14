'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { OrderStatusBadge } from '../cells/OrderStatusBadge';
import type { Order, OrderStatus } from '@/types/sales';

interface StatusUpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  order: Order;
  onSubmit: (data: {
    newStatus: OrderStatus;
    note?: string;
    notifyCustomer: boolean;
  }) => Promise<void>;
}

const validTransitions: Record<string, OrderStatus[]> = {
  DRAFT: ['CONFIRMED', 'CANCELLED'],
  PENDING: ['CONFIRMED', 'CANCELLED'],
  CONFIRMED: ['PROCESSING', 'CANCELLED'],
  PROCESSING: ['SHIPPED', 'CANCELLED'],
  SHIPPED: ['DELIVERED'],
  DELIVERED: [],
  COMPLETED: [],
  CANCELLED: [],
  REFUNDED: [],
};

const statusUpdateSchema = z.object({
  newStatus: z.string().min(1, 'Please select a status'),
  note: z.string().max(500).optional(),
  notifyCustomer: z.boolean(),
});

type StatusUpdateFormData = z.infer<typeof statusUpdateSchema>;

export function StatusUpdateModal({ isOpen, onClose, order, onSubmit }: StatusUpdateModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const availableTransitions = validTransitions[order.orderStatus] || [];

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors },
  } = useForm<StatusUpdateFormData>({
    resolver: zodResolver(statusUpdateSchema),
    defaultValues: {
      newStatus: '',
      note: '',
      notifyCustomer: true,
    },
  });

  const note = watch('note');
  const charCount = note?.length || 0;

  const handleFormSubmit = async (data: StatusUpdateFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit({
        newStatus: data.newStatus as OrderStatus,
        note: data.note || undefined,
        notifyCustomer: data.notifyCustomer,
      });
      reset();
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Update Order Status</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          {/* Current Status */}
          <div>
            <Label className="text-sm text-gray-500">Current Status</Label>
            <div className="mt-1">
              <OrderStatusBadge status={order.orderStatus} />
            </div>
          </div>

          {/* New Status */}
          <div>
            <Label>New Status</Label>
            {availableTransitions.length === 0 ? (
              <p className="mt-1 text-sm text-gray-500">
                No status transitions available from {order.orderStatus.replace(/_/g, ' ')}.
              </p>
            ) : (
              <Select onValueChange={(val) => setValue('newStatus', val)}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  {availableTransitions.map((status) => (
                    <SelectItem key={status} value={status}>
                      {status.replace(/_/g, ' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
            {errors.newStatus && (
              <p className="mt-1 text-xs text-red-500">{errors.newStatus.message}</p>
            )}
          </div>

          {/* Note */}
          <div>
            <Label>Note (optional)</Label>
            <Textarea
              placeholder="Add a note about this status change..."
              rows={3}
              {...register('note')}
              className="mt-1"
            />
            <div className="mt-1 flex justify-end">
              <span className={`text-xs ${charCount > 450 ? 'text-orange-500' : 'text-gray-400'}`}>
                {charCount} / 500
              </span>
            </div>
          </div>

          {/* Notify Customer */}
          <div className="flex items-center gap-2">
            <Checkbox
              id="notifyCustomer"
              defaultChecked
              onCheckedChange={(checked) => setValue('notifyCustomer', checked === true)}
            />
            <Label htmlFor="notifyCustomer" className="text-sm font-normal">
              Notify customer via email
            </Label>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting || availableTransitions.length === 0}>
              {isSubmitting ? 'Updating...' : 'Update Status'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
