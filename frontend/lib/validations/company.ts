import { z } from 'zod';

const companyAddressSchema = z.object({
  street: z.string().min(1, 'Street address is required'),
  city: z.string().min(1, 'City is required'),
  province: z.string().min(1, 'Province is required'),
  postalCode: z
    .string()
    .min(1, 'Postal code is required')
    .regex(/^\d{5}$/, 'Postal code must be 5 digits'),
  country: z.string().min(1, 'Country is required'),
});

export const companyFormSchema = z.object({
  name: z
    .string()
    .min(2, 'Company name must be at least 2 characters')
    .max(200, 'Company name must be at most 200 characters'),
  logo: z.string().optional(),
  address: companyAddressSchema,
  tin: z.string().optional(),
  vatNumber: z.string().optional(),
  taxRegistrationType: z.string().optional(),
  phone: z
    .string()
    .min(1, 'Phone number is required')
    .regex(/^\+94\d{9}$/, 'Phone must be in +94XXXXXXXXX format'),
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  website: z
    .string()
    .optional()
    .refine(
      (val) => !val || /^https?:\/\//.test(val),
      'Website must start with http:// or https://'
    ),
});

export type CompanyFormValues = z.infer<typeof companyFormSchema>;
