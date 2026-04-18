'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from '../Information/FormFieldError';

export const AddressLine1Input = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="address1">
        Street Address <span className="text-red-500">*</span>
      </Label>
      <Input
        id="address1"
        type="text"
        autoComplete="address-line1"
        placeholder="123 Main Street"
        {...register('address1')}
      />
      <FormFieldError fieldName="address1" />
    </div>
  );
};
