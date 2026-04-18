import { z } from 'zod';

export const registerSchema = z
  .object({
    registrationMethod: z.enum(['email', 'phone']).default('email'),
    email: z.string().email('Please enter a valid email address').optional().or(z.literal('')),
    phone: z
      .string()
      .optional()
      .or(z.literal('')),
    firstName: z
      .string()
      .min(2, 'First name must be at least 2 characters')
      .max(50, 'First name must be at most 50 characters'),
    lastName: z
      .string()
      .min(2, 'Last name must be at least 2 characters')
      .max(50, 'Last name must be at most 50 characters'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number')
      .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),
    confirmPassword: z.string(),
    termsAccepted: z.boolean().refine((val) => val === true, {
      message: 'You must accept the terms',
    }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })
  .refine(
    (data) => {
      if (data.registrationMethod === 'email') {
        return !!data.email && data.email.length > 0;
      }
      return true;
    },
    {
      message: 'Email is required',
      path: ['email'],
    },
  )
  .refine(
    (data) => {
      if (data.registrationMethod === 'phone') {
        return !!data.phone && /^\+94\d{9}$/.test(data.phone);
      }
      return true;
    },
    {
      message: 'Please enter a valid Sri Lanka phone number (+94XXXXXXXXX)',
      path: ['phone'],
    },
  );

export type RegisterFormValues = z.infer<typeof registerSchema>;
