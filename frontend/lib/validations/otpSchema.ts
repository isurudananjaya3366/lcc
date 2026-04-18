import { z } from 'zod';

export const otpSchema = z.object({
  otp: z
    .string()
    .length(6, 'OTP must be 6 digits')
    .regex(/^\d{6}$/, 'OTP must be numeric'),
});

export type OTPFormValues = z.infer<typeof otpSchema>;
