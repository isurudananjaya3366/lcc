import { z } from 'zod';

export const inviteUserSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Invalid email address'),
  roleId: z.string().min(1, 'Role is required'),
  message: z.string().max(500, 'Message too long').optional(),
});

export type InviteUserInput = z.infer<typeof inviteUserSchema>;
