'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { CustomerFormValues } from '@/lib/validations/customer';

interface CustomerAddressFieldsProps {
  register: UseFormRegister<CustomerFormValues>;
  errors: FieldErrors<CustomerFormValues>;
}

export function CustomerAddressFields({ register, errors }: CustomerAddressFieldsProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Address</h3>
      <div className="space-y-2">
        <Label htmlFor="addressStreet">Street Address</Label>
        <Input id="addressStreet" {...register('addressStreet')} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="addressCity">City</Label>
          <Input id="addressCity" {...register('addressCity')} />
        </div>
        <div className="space-y-2">
          <Label htmlFor="addressState">District</Label>
          <Input id="addressState" {...register('addressState')} placeholder="e.g., Colombo" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="addressPostalCode">Postal Code</Label>
          <Input id="addressPostalCode" {...register('addressPostalCode')} placeholder="00100" />
          {errors.addressPostalCode && (
            <p className="text-xs text-destructive">{errors.addressPostalCode.message}</p>
          )}
        </div>
        <div className="space-y-2">
          <Label htmlFor="addressCountry">Country</Label>
          <Input id="addressCountry" {...register('addressCountry')} defaultValue="Sri Lanka" />
        </div>
      </div>
    </div>
  );
}
