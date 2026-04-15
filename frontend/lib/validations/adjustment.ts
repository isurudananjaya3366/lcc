import { z } from 'zod';
import { AdjustmentReason } from '@/types/inventory';

export const adjustmentItemSchema = z.object({
  productId: z.string().min(1, 'Product is required'),
  variantId: z.string().optional(),
  currentQuantity: z.number().min(0),
  newQuantity: z.number().min(0, 'Quantity must be non-negative'),
  notes: z.string().max(500).optional(),
});

export const adjustmentFormSchema = z.object({
  warehouseId: z.string().min(1, 'Warehouse is required'),
  reason: z.nativeEnum(AdjustmentReason, {
    error: 'Reason is required',
  }),
  reasonNotes: z.string().max(500).optional(),
  items: z.array(adjustmentItemSchema).min(1, 'At least one product must be added'),
});

export type AdjustmentFormValues = z.infer<typeof adjustmentFormSchema>;
export type AdjustmentItemValues = z.infer<typeof adjustmentItemSchema>;
