import { z } from 'zod';
import { EmploymentType } from '@/types/hr';

// Sri Lankan NIC: old format (9 digits + V/X) or new format (12 digits)
const nicRegex = /^([0-9]{9}[VvXx]|[0-9]{12})$/;

export const employeeFormSchema = z.object({
  firstName: z.string().min(2, 'First name must be at least 2 characters').max(100),
  lastName: z.string().min(2, 'Last name must be at least 2 characters').max(100),
  email: z.string().email('Enter a valid email address'),
  phone: z
    .string()
    .regex(/^0[0-9]{9}$/, 'Enter a valid Sri Lankan phone number (e.g., 0711234567)')
    .optional()
    .or(z.literal('')),
  nic: z
    .string()
    .regex(nicRegex, 'Enter a valid NIC (old: 9 digits + V/X, new: 12 digits)')
    .optional()
    .or(z.literal('')),
  dateOfBirth: z.string().optional().or(z.literal('')),
  gender: z.string().optional(),
  nationality: z.string().optional(),
  employmentType: z.nativeEnum(EmploymentType),
  departmentId: z.string().min(1, 'Department is required'),
  positionId: z.string().min(1, 'Position is required'),
  hireDate: z.string().min(1, 'Hire date is required'),
  probationEndDate: z.string().optional().or(z.literal('')),
  managerId: z.string().optional(),
  workLocation: z.string().optional(),
  addressLine1: z.string().optional(),
  addressLine2: z.string().optional(),
  city: z.string().optional(),
  district: z.string().optional(),
  emergencyContactName: z.string().optional(),
  emergencyContactRelationship: z.string().optional(),
  emergencyContactPhone: z
    .string()
    .regex(/^0[0-9]{9}$/, 'Enter a valid phone number')
    .optional()
    .or(z.literal('')),
  bankName: z.string().optional(),
  bankAccountNumber: z.string().optional(),
  taxId: z.string().optional(),
  salary: z.number().min(0, 'Salary must be non-negative').optional(),
});

export type EmployeeFormValues = z.infer<typeof employeeFormSchema>;
