'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from '../Information/FormFieldError';

export const PostalCodeInput = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="postalCode">
        Postal Code <span className="text-red-500">*</span>
      </Label>
      <Input
        id="postalCode"
        type="text"
        inputMode="numeric"
        autoComplete="postal-code"
        placeholder="10100"
        maxLength={5}
        {...register('postalCode')}
      />
      <FormFieldError fieldName="postalCode" />
    </div>
  );
};
