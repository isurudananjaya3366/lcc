'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from './FormFieldError';

export const EmailInput = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="email">
        Email <span className="text-red-500">*</span>
      </Label>
      <Input
        id="email"
        type="email"
        autoComplete="email"
        inputMode="email"
        placeholder="your.email@example.com"
        {...register('email')}
      />
      <FormFieldError fieldName="email" />
    </div>
  );
};
