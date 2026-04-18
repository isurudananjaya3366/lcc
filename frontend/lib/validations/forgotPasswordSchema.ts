import { z } from 'zod';

export const forgotPasswordSchema = z.object({
  identifier: z.string().min(1, 'Email or phone is required'),
});

export type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;
