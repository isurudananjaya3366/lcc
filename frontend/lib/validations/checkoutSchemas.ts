import { z } from 'zod';

export const informationStepSchema = z.object({
  email: z
    .string()
    .trim()
    .toLowerCase()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  phone: z
    .string()
    .min(1, 'Phone number is required')
    .regex(/^7[0-9]{8}$/, 'Enter a valid 9-digit Sri Lankan mobile number starting with 7'),
  firstName: z
    .string()
    .trim()
    .min(2, 'First name must be at least 2 characters')
    .max(50, 'First name must be at most 50 characters'),
  lastName: z
    .string()
    .trim()
    .min(2, 'Last name must be at least 2 characters')
    .max(50, 'Last name must be at most 50 characters'),
  whatsappOptIn: z.boolean().default(true),
});

export type InformationStepData = z.infer<typeof informationStepSchema>;

export const shippingStepSchema = z.object({
  province: z.string().min(1, 'Province is required'),
  district: z.string().min(1, 'District is required'),
  city: z.string().min(1, 'City is required'),
  address1: z
    .string()
    .min(1, 'Address is required')
    .max(100, 'Address must be at most 100 characters'),
  address2: z.string().optional().default(''),
  landmark: z.string().optional().default(''),
  postalCode: z.string().regex(/^[0-9]{5}$/, 'Valid 5-digit postal code required'),
  shippingMethodId: z.string().min(1, 'Shipping method is required'),
});

export type ShippingStepData = z.infer<typeof shippingStepSchema>;

export const paymentStepSchema = z.object({
  methodType: z.enum(['payhere', 'card', 'bank_transfer', 'cod', 'koko', 'mintpay']),
  bankReceipt: z.string().optional(),
});

export type PaymentStepData = z.infer<typeof paymentStepSchema>;
