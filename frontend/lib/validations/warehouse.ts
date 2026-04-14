import { z } from 'zod';

export const warehouseFormSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be at most 100 characters'),
  code: z
    .string()
    .min(2, 'Code is required')
    .max(10, 'Code must be at most 10 characters')
    .regex(/^[A-Z0-9-]+$/, 'Code must be uppercase letters, numbers, or hyphens'),
  description: z.string().max(500).optional(),
  address: z.object({
    street: z.string().min(1, 'Address line 1 is required'),
    street2: z.string().optional(),
    city: z.string().min(1, 'City is required'),
    state: z.string().min(1, 'District is required'),
    postalCode: z.string().optional(),
    country: z.string().default('LK'),
  }),
  contactPhone: z.string().max(20).optional(),
  contactEmail: z.string().email('Invalid email').optional().or(z.literal('')),
  capacity: z.number().min(0).optional(),
  isPrimary: z.boolean().default(false),
  isActive: z.boolean().default(true),
});

export type WarehouseFormValues = z.infer<typeof warehouseFormSchema>;

export const warehouseFormDefaults: WarehouseFormValues = {
  name: '',
  code: '',
  description: '',
  address: {
    street: '',
    street2: '',
    city: '',
    state: '',
    postalCode: '',
    country: 'LK',
  },
  contactPhone: '',
  contactEmail: '',
  capacity: undefined,
  isPrimary: false,
  isActive: true,
};
