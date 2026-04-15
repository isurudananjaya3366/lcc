import { z } from 'zod';

export const paymentMethods = [
  { value: 'CASH', label: 'Cash', icon: 'Banknote' },
  { value: 'BANK_TRANSFER', label: 'Bank Transfer', icon: 'Building2' },
  { value: 'CREDIT_CARD', label: 'Credit Card', icon: 'CreditCard' },
  { value: 'DEBIT_CARD', label: 'Debit Card', icon: 'CreditCard' },
  { value: 'CHEQUE', label: 'Cheque', icon: 'FileText' },
  { value: 'ONLINE', label: 'Online', icon: 'Globe' },
] as const;

export type PaymentMethodValue = (typeof paymentMethods)[number]['value'];

export const paymentFormSchema = z.object({
  paymentMethod: z.enum(
    ['CASH', 'BANK_TRANSFER', 'CREDIT_CARD', 'DEBIT_CARD', 'CHEQUE', 'ONLINE'],
    { message: 'Payment method is required' }
  ),
  amount: z.coerce.number({ message: 'Amount is required' }).positive('Amount must be positive'),
  referenceNumber: z.string().max(100, 'Max 100 characters').optional(),
  paymentDate: z.string().min(1, 'Payment date is required'),
  notes: z.string().max(500, 'Max 500 characters').optional(),
});

export type PaymentFormValues = z.infer<typeof paymentFormSchema>;
