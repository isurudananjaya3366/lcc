import { z } from 'zod';

// ── Step 1: Business Info ─────────────────────────────────────

export const businessInfoSchema = z.object({
  businessName: z
    .string()
    .min(2, 'Business name must be at least 2 characters')
    .max(100, 'Business name must be at most 100 characters'),
  businessType: z.enum(
    ['retail', 'wholesale', 'restaurant', 'service', 'manufacturing', 'ecommerce'],
    { message: 'Please select a business type' }
  ),
  registrationNumber: z.string().max(50).optional().or(z.literal('')),
});

// ── Step 2: Admin User ────────────────────────────────────────

export const adminUserBaseSchema = z.object({
    firstName: z
      .string()
      .min(2, 'First name must be at least 2 characters')
      .max(50, 'First name must be at most 50 characters'),
    lastName: z
      .string()
      .min(2, 'Last name must be at least 2 characters')
      .max(50, 'Last name must be at most 50 characters'),
    email: z.string().min(1, 'Email is required').email('Please enter a valid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  });

export const adminUserSchema = adminUserBaseSchema
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

// ── Step 3: Contact Info ──────────────────────────────────────

export const contactInfoSchema = z.object({
  phone: z
    .string()
    .min(1, 'Phone number is required')
    .regex(
      /^\+94\s?\d{2}\s?\d{3}\s?\d{4}$/,
      'Please enter a valid Sri Lankan phone number (+94 XX XXX XXXX)'
    ),
  address: z
    .object({
      street: z.string().max(200).optional().or(z.literal('')),
      city: z.string().max(50).optional().or(z.literal('')),
      postalCode: z
        .string()
        .regex(/^\d{5}$/, 'Postal code must be 5 digits')
        .optional()
        .or(z.literal('')),
    })
    .optional(),
  timezone: z.string().min(1, 'Timezone is required').default('Asia/Colombo'),
});

// ── Step 4: Plan Selection ────────────────────────────────────

export const planSelectionSchema = z.object({
  plan: z.enum(['starter', 'professional', 'enterprise'], {
    message: 'Please select a plan',
  }),
});

// ── Terms Acceptance ──────────────────────────────────────────

export const termsSchema = z.object({
  acceptTerms: z.literal(true, {
    error: 'You must accept the terms and conditions',
  }),
});

// ── Combined Registration Schema ──────────────────────────────

export const registrationSchema = businessInfoSchema
  .merge(adminUserBaseSchema)
  .merge(contactInfoSchema)
  .merge(planSelectionSchema)
  .merge(termsSchema)
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  });

// ── Types ─────────────────────────────────────────────────────

export type BusinessInfoData = z.infer<typeof businessInfoSchema>;
export type AdminUserData = z.infer<typeof adminUserSchema>;
export type ContactInfoData = z.infer<typeof contactInfoSchema>;
export type PlanSelectionData = z.infer<typeof planSelectionSchema>;
export type RegistrationFormData = z.infer<typeof registrationSchema>;
