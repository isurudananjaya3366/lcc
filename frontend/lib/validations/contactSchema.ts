import { z } from 'zod';

export const contactSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  email: z.string().email('Invalid email address'),
  phone: z.string().optional().or(z.literal('')),
  subject: z.string().optional().or(z.literal('')),
  message: z.string().min(10, 'Message must be at least 10 characters').max(2000),
});

export type ContactFormValues = z.infer<typeof contactSchema>;
