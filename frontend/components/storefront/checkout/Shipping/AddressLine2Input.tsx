'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from '../Information/FormFieldError';

export const AddressLine2Input = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="address2">Apartment, Suite, etc.</Label>
      <Input
        id="address2"
        type="text"
        autoComplete="address-line2"
        placeholder="Apt 4B, Suite 100, etc."
        {...register('address2')}
      />
      <FormFieldError fieldName="address2" />
    </div>
  );
};
