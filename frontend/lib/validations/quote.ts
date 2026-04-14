/**
 * Zod validation schemas for the Quote form
 */

import { z } from 'zod';

export const quoteItemSchema = z.object({
  productId: z.string().min(1, 'Product is required'),
  variantId: z.string().optional(),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  unitPrice: z.number().positive('Price must be greater than 0'),
  discountPercent: z.number().min(0).max(100).default(0),
});

export const quoteFormSchema = z.object({
  customerId: z.string().min(1, 'Customer is required'),
  expiryDate: z.string().min(1, 'Expiry date is required'),
  items: z.array(quoteItemSchema).min(1, 'At least one item is required'),
  terms: z.string().max(2000).optional(),
  notes: z.string().max(1000).optional(),
});

export type QuoteFormValues = z.infer<typeof quoteFormSchema>;
export type QuoteItemValues = z.infer<typeof quoteItemSchema>;
