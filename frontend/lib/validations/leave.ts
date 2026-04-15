import { z } from 'zod';

export const leaveRequestSchema = z
  .object({
    leaveType: z.string().min(1, 'Leave type is required'),
    startDate: z.string().min(1, 'Start date is required'),
    endDate: z.string().min(1, 'End date is required'),
    reason: z
      .string()
      .min(10, 'Reason must be at least 10 characters')
      .max(500, 'Reason must be at most 500 characters')
      .optional()
      .or(z.literal('')),
    halfDay: z.boolean().optional(),
    halfDayPeriod: z.enum(['morning', 'afternoon']).optional(),
    attachments: z.array(z.string()).optional(),
    emergencyContact: z.string().optional(),
    handoverNotes: z.string().max(1000).optional().or(z.literal('')),
    isConfidential: z.boolean().optional(),
  })
  .refine(
    (data) => {
      if (!data.startDate || !data.endDate) return true;
      return data.startDate <= data.endDate;
    },
    { message: 'End date must be after start date', path: ['endDate'] }
  );

export type LeaveRequestFormValues = z.infer<typeof leaveRequestSchema>;
