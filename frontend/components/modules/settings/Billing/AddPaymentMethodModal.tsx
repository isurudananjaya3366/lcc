'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';

const addPaymentMethodSchema = z.object({
  cardNumber: z
    .string()
    .min(15, 'Card number must be at least 15 digits')
    .max(19, 'Card number must be at most 19 digits')
    .regex(/^\d+$/, 'Card number must contain only digits'),
  expiryMonth: z.string().regex(/^(0[1-9]|1[0-2])$/, 'Invalid month (01-12)'),
  expiryYear: z
    .string()
    .regex(/^\d{4}$/, 'Invalid year')
    .refine((val) => parseInt(val) >= new Date().getFullYear(), 'Card has expired'),
  cvc: z
    .string()
    .min(3, 'CVC must be 3-4 digits')
    .max(4, 'CVC must be 3-4 digits')
    .regex(/^\d+$/, 'CVC must contain only digits'),
  cardholderName: z.string().min(1, 'Cardholder name is required').max(100),
  setAsDefault: z.boolean(),
});

type AddPaymentMethodFormValues = z.infer<typeof addPaymentMethodSchema>;

interface AddPaymentMethodModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function AddPaymentMethodModal({ isOpen, onClose, onSuccess }: AddPaymentMethodModalProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<AddPaymentMethodFormValues>({
    resolver: zodResolver(addPaymentMethodSchema),
    defaultValues: {
      cardNumber: '',
      expiryMonth: '',
      expiryYear: '',
      cvc: '',
      cardholderName: '',
      setAsDefault: false,
    },
  });

  const handleSubmit = async (values: AddPaymentMethodFormValues) => {
    setIsSubmitting(true);
    try {
      // In production: POST /api/billing/payment-methods with tokenized data
      console.log('Adding payment method:', {
        last4: values.cardNumber.slice(-4),
        expiryMonth: values.expiryMonth,
        expiryYear: values.expiryYear,
        cardholderName: values.cardholderName,
        setAsDefault: values.setAsDefault,
      });
      await new Promise((resolve) => setTimeout(resolve, 1000));
      onSuccess();
      onClose();
      form.reset();
    } catch {
      console.error('Failed to add payment method');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Payment Method</DialogTitle>
          <DialogDescription>Add a new credit or debit card for billing.</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="cardNumber"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Card Number</FormLabel>
                  <FormControl>
                    <Input placeholder="1234567890123456" maxLength={19} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-3 gap-3">
              <FormField
                control={form.control}
                name="expiryMonth"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Month</FormLabel>
                    <FormControl>
                      <Input placeholder="MM" maxLength={2} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="expiryYear"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Year</FormLabel>
                    <FormControl>
                      <Input placeholder="YYYY" maxLength={4} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="cvc"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>CVC</FormLabel>
                    <FormControl>
                      <Input placeholder="123" maxLength={4} {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="cardholderName"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Cardholder Name</FormLabel>
                  <FormControl>
                    <Input placeholder="Name on card" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="setAsDefault"
              render={({ field }) => (
                <FormItem className="flex items-center gap-2 space-y-0">
                  <FormControl>
                    <Checkbox checked={field.value} onCheckedChange={field.onChange} />
                  </FormControl>
                  <FormLabel className="font-normal">Set as default payment method</FormLabel>
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Adding...' : 'Add Card'}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
