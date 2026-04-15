import { z } from 'zod';

const poLineItemSchema = z.object({
  productId: z.string().min(1, 'Product is required'),
  variantId: z.string().optional(),
  quantity: z.number().min(1, 'Quantity must be at least 1'),
  unitCost: z.number().min(0, 'Unit cost must be positive'),
});

export const poFormSchema = z.object({
  vendorId: z.string().min(1, 'Vendor is required'),
  orderDate: z.string().min(1, 'Order date is required'),
  expectedDate: z.string().optional(),
  items: z.array(poLineItemSchema).min(1, 'At least one item is required'),
  notes: z.string().max(2000).optional(),
  terms: z.string().max(2000).optional(),
  shipping: z.number().min(0).optional(),
  tax: z.number().min(0).optional(),
});

export type POFormValues = z.infer<typeof poFormSchema>;
export type POLineItemValues = z.infer<typeof poLineItemSchema>;
