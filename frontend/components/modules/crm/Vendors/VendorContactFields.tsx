'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { UseFormRegister, FieldErrors } from 'react-hook-form';
import type { VendorFormValues } from '@/lib/validations/vendor';

interface VendorContactFieldsProps {
  register: UseFormRegister<VendorFormValues>;
  errors: FieldErrors<VendorFormValues>;
}

export function VendorContactFields({ register, errors }: VendorContactFieldsProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Contact Details</h3>

      <div className="space-y-2">
        <Label htmlFor="contactName">Contact Person Name *</Label>
        <Input id="contactName" {...register('contactName')} />
        {errors.contactName && (
          <p className="text-xs text-destructive">{errors.contactName.message}</p>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="phone">Phone *</Label>
          <Input id="phone" {...register('phone')} placeholder="0711234567" />
          {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
          <p className="text-xs text-muted-foreground">Format: 0XX XXX XXXX</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="email">Email *</Label>
          <Input id="email" type="email" {...register('email')} />
          {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="website">Website</Label>
        <Input id="website" {...register('website')} placeholder="https://" />
        {errors.website && <p className="text-xs text-destructive">{errors.website.message}</p>}
      </div>
    </div>
  );
}
