import { z } from 'zod';

export const transferItemSchema = z.object({
  productId: z.string().min(1, 'Product is required'),
  variantId: z.string().optional(),
  availableQuantity: z.number().min(0),
  quantity: z.number().min(1, 'Quantity must be at least 1').int('Quantity must be a whole number'),
  notes: z.string().max(500).optional(),
});

export const transferFormSchema = z
  .object({
    sourceWarehouseId: z.string().min(1, 'Source warehouse is required'),
    destinationWarehouseId: z.string().min(1, 'Destination warehouse is required'),
    expectedDate: z.string().optional(),
    notes: z.string().max(1000).optional(),
    items: z.array(transferItemSchema).min(1, 'At least one item is required'),
  })
  .refine((data) => data.sourceWarehouseId !== data.destinationWarehouseId, {
    message: 'Source and destination warehouses must be different',
    path: ['destinationWarehouseId'],
  });

export type TransferFormValues = z.infer<typeof transferFormSchema>;
export type TransferItemValues = z.infer<typeof transferItemSchema>;
