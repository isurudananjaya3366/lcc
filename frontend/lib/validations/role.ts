import { z } from 'zod';

export const roleSchema = z.object({
  name: z
    .string()
    .min(2, 'Role name must be at least 2 characters')
    .max(50, 'Role name must be at most 50 characters'),
  description: z.string().max(200, 'Description must be at most 200 characters').optional(),
  permissions: z.array(z.string()),
});

export type RoleFormValues = z.infer<typeof roleSchema>;
