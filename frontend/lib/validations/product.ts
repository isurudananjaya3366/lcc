import { z } from 'zod';

const ACCEPTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5MB
const MAX_IMAGES = 10;

const skuPattern = /^[A-Z0-9-]+$/;

export const productFormSchema = z
  .object({
    // Basic Information
    name: z
      .string()
      .trim()
      .min(2, 'Product name must be at least 2 characters')
      .max(200, 'Product name must not exceed 200 characters'),
    sku: z
      .string()
      .min(1, 'SKU is required')
      .max(30, 'SKU must not exceed 30 characters')
      .regex(skuPattern, 'SKU must contain only uppercase letters, numbers, and dashes'),
    description: z
      .string()
      .trim()
      .max(5000, 'Description must not exceed 5000 characters')
      .optional()
      .or(z.literal('')),

    // Pricing
    cost_price: z
      .number({ message: 'Cost price must be a number' })
      .min(0, 'Cost price must be 0 or greater')
      .transform((v) => Math.round(v * 100) / 100),
    selling_price: z
      .number({ message: 'Selling price must be a number' })
      .min(0, 'Selling price must be 0 or greater')
      .transform((v) => Math.round(v * 100) / 100),
    tax_category_id: z.string().optional().or(z.literal('')),

    // Inventory
    track_inventory: z.boolean().default(true),
    initial_stock: z
      .number({ message: 'Initial stock must be a number' })
      .int('Initial stock must be a whole number')
      .min(0, 'Initial stock must be 0 or greater')
      .optional(),
    reorder_point: z
      .number({ message: 'Reorder point must be a number' })
      .int('Reorder point must be a whole number')
      .min(0, 'Reorder point must be 0 or greater')
      .optional(),

    // Categorization
    category_ids: z.array(z.string()).optional().default([]),
    tags: z
      .array(
        z
          .string()
          .min(2, 'Tag must be at least 2 characters')
          .max(30, 'Tag must not exceed 30 characters')
      )
      .max(20, 'Maximum 20 tags allowed')
      .optional()
      .default([]),

    // Media
    images: z
      .array(z.instanceof(File))
      .max(MAX_IMAGES, `Maximum ${MAX_IMAGES} images allowed`)
      .refine(
        (files) => files.every((file) => ACCEPTED_IMAGE_TYPES.includes(file.type)),
        'Only JPEG, PNG, and WebP images are accepted'
      )
      .refine(
        (files) => files.every((file) => file.size <= MAX_IMAGE_SIZE),
        'Each image must be 5MB or smaller'
      )
      .optional()
      .default([]),
  })
  .refine((data) => data.selling_price >= data.cost_price, {
    message: 'Selling price must be greater than or equal to cost price',
    path: ['selling_price'],
  })
  .refine(
    (data) => {
      if (
        data.track_inventory &&
        (data.initial_stock === undefined || data.initial_stock === null)
      ) {
        return false;
      }
      return true;
    },
    {
      message: 'Initial stock is required when inventory tracking is enabled',
      path: ['initial_stock'],
    }
  );

export type ProductFormData = z.infer<typeof productFormSchema>;

export const productFormDefaults: Partial<ProductFormData> = {
  name: '',
  sku: '',
  description: '',
  cost_price: 0,
  selling_price: 0,
  tax_category_id: '',
  track_inventory: true,
  initial_stock: 0,
  reorder_point: 0,
  category_ids: [],
  tags: [],
  images: [],
};
