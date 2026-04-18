'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from './FormFieldError';

export const FirstNameInput = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="firstName">
        First Name <span className="text-red-500">*</span>
      </Label>
      <Input
        id="firstName"
        autoComplete="given-name"
        placeholder="First name"
        {...register('firstName')}
      />
      <FormFieldError fieldName="firstName" />
    </div>
  );
};
