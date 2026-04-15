import { z } from 'zod';

export const vendorFormSchema = z.object({
  companyName: z.string().min(2, 'Name must be at least 2 characters').max(200),
  vendorType: z.enum(['SUPPLIER', 'MANUFACTURER', 'DISTRIBUTOR', 'SERVICE_PROVIDER', 'CONTRACTOR']),
  category: z.enum(['RAW_MATERIALS', 'FINISHED_GOODS', 'SERVICES', 'EQUIPMENT', 'UTILITIES']),
  contactName: z.string().min(2, 'Contact name is required'),
  phone: z
    .string()
    .regex(/^0[0-9]{9}$/, 'Enter a valid Sri Lankan phone number (e.g., 0711234567)'),
  email: z.string().email('Enter a valid email address'),
  website: z.string().url('Enter a valid URL').optional().or(z.literal('')),
  address: z.string().optional(),
  city: z.string().optional(),
  postalCode: z.string().optional(),
  paymentTerms: z
    .enum(['NET_7', 'NET_15', 'NET_30', 'NET_45', 'NET_60', 'NET_90', 'COD', 'PREPAID'])
    .optional(),
  currency: z.enum(['LKR', 'USD']).optional(),
  leadTime: z.number().min(0, 'Lead time must be positive').optional(),
  minOrderAmount: z.number().min(0, 'Minimum order must be positive').optional(),
});

export type VendorFormValues = z.infer<typeof vendorFormSchema>;
