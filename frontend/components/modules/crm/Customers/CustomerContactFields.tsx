'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { CustomerFormValues } from '@/lib/validations/customer';

interface CustomerContactFieldsProps {
  register: UseFormRegister<CustomerFormValues>;
  errors: FieldErrors<CustomerFormValues>;
}

export function CustomerContactFields({ register, errors }: CustomerContactFieldsProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Contact Details</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="phone">Phone</Label>
          <Input id="phone" {...register('phone')} placeholder="0711234567" />
          {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="mobile">Mobile</Label>
          <Input id="mobile" {...register('mobile')} placeholder="0771234567" />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" {...register('email')} placeholder="customer@example.com" />
        {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
      </div>
      <div className="space-y-2">
        <Label htmlFor="taxId">Tax ID (NIC/TIN)</Label>
        <Input id="taxId" {...register('taxId')} placeholder="Tax identification number" />
      </div>
    </div>
  );
}
