import { z } from 'zod';

export const customerFormSchema = z
  .object({
    customerType: z.enum(['INDIVIDUAL', 'BUSINESS', 'WHOLESALER', 'DISTRIBUTOR']),
    firstName: z.string().optional(),
    lastName: z.string().optional(),
    companyName: z.string().optional(),
    displayName: z.string().min(2, 'Display name must be at least 2 characters').max(200),
    email: z.string().email('Enter a valid email address').optional().or(z.literal('')),
    phone: z
      .string()
      .regex(/^0[0-9]{9}$/, 'Enter a valid Sri Lankan phone number (e.g., 0711234567)')
      .optional()
      .or(z.literal('')),
    mobile: z.string().optional().or(z.literal('')),
    taxId: z.string().optional(),
    // Address fields
    addressStreet: z.string().optional(),
    addressCity: z.string().optional(),
    addressState: z.string().optional(),
    addressPostalCode: z
      .string()
      .regex(/^\d{5}$/, 'Postal code must be 5 digits')
      .optional()
      .or(z.literal('')),
    addressCountry: z.string().optional(),
    // Credit
    creditLimit: z.number().min(0, 'Credit limit must be non-negative').optional(),
    paymentTerms: z
      .enum(['NET_0', 'NET_15', 'NET_30', 'NET_45', 'NET_60', 'COD', 'PREPAID'])
      .optional(),
    // Notes
    notes: z.string().max(2000).optional(),
  })
  .refine(
    (data) => {
      if (data.customerType === 'INDIVIDUAL') {
        return !!data.firstName;
      }
      return !!data.companyName;
    },
    {
      message: 'First name is required for individuals, company name for businesses',
      path: ['firstName'],
    }
  );

export type CustomerFormValues = z.infer<typeof customerFormSchema>;
