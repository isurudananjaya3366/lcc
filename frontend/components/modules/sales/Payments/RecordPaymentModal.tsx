'use client';

import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { paymentFormSchema, type PaymentFormValues } from '@/lib/validations/payment';
import { PaymentMethodSelect } from './PaymentMethodSelect';
import { AmountInput } from './AmountInput';
import { ReferenceNumberInput } from './ReferenceNumberInput';
import { PaymentDatePicker } from './PaymentDatePicker';
import { PaymentNotesField } from './PaymentNotesField';
import type { PaymentStatus } from '@/types/sales';

interface RecordPaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: string;
  orderNumber: string;
  orderTotal: number;
  amountPaid: number;
  paymentStatus: PaymentStatus;
  isSubmitting?: boolean;
  onSubmit: (data: PaymentFormValues) => void;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

function toISODate(date: Date): string {
  return date.toISOString().split('T')[0];
}

export function RecordPaymentModal({
  isOpen,
  onClose,
  orderNumber,
  orderTotal,
  amountPaid,
  isSubmitting,
  onSubmit,
}: RecordPaymentModalProps) {
  const amountDue = Math.max(0, orderTotal - amountPaid);

  const {
    control,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm<PaymentFormValues>({
    resolver: zodResolver(paymentFormSchema),
    defaultValues: {
      paymentMethod: undefined,
      amount: amountDue,
      referenceNumber: '',
      paymentDate: toISODate(new Date()),
      notes: '',
    },
  });

  const selectedMethod = watch('paymentMethod');

  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Record Payment</DialogTitle>
        </DialogHeader>

        {/* Order Summary */}
        <div className="rounded-md border bg-gray-50 p-3 text-sm dark:bg-gray-800">
          <div className="flex justify-between">
            <span className="text-gray-500">Order</span>
            <span className="font-mono font-medium">{orderNumber}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Order Total</span>
            <span>{formatCurrency(orderTotal)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Paid</span>
            <span>{formatCurrency(amountPaid)}</span>
          </div>
          <div className="flex justify-between border-t pt-1 font-medium">
            <span>Balance Due</span>
            <span className={amountDue > 0 ? 'text-red-600' : 'text-green-600'}>
              {formatCurrency(amountDue)}
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Controller
            name="paymentMethod"
            control={control}
            render={({ field }) => (
              <PaymentMethodSelect
                value={field.value}
                onChange={field.onChange}
                error={errors.paymentMethod?.message}
              />
            )}
          />

          <Controller
            name="amount"
            control={control}
            render={({ field }) => (
              <AmountInput
                value={field.value}
                onChange={field.onChange}
                amountDue={amountDue}
                error={errors.amount?.message}
              />
            )}
          />

          <Controller
            name="referenceNumber"
            control={control}
            render={({ field }) => (
              <ReferenceNumberInput
                value={field.value}
                onChange={field.onChange}
                paymentMethod={selectedMethod}
                error={errors.referenceNumber?.message}
              />
            )}
          />

          <Controller
            name="paymentDate"
            control={control}
            render={({ field }) => (
              <PaymentDatePicker
                value={field.value}
                onChange={field.onChange}
                error={errors.paymentDate?.message}
              />
            )}
          />

          <Controller
            name="notes"
            control={control}
            render={({ field }) => (
              <PaymentNotesField
                value={field.value}
                onChange={field.onChange}
                error={errors.notes?.message}
              />
            )}
          />

          <DialogFooter className="gap-2">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Recording...' : 'Record Payment'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
