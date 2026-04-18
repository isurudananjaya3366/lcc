'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from './FormFieldError';

export const PhoneInput = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="phone">
        Phone <span className="text-red-500">*</span>
      </Label>
      <div className="flex">
        <span className="inline-flex items-center rounded-l-md border border-r-0 border-input bg-muted px-3 text-sm text-muted-foreground">
          +94
        </span>
        <Input
          id="phone"
          type="tel"
          inputMode="tel"
          autoComplete="tel-national"
          placeholder="7X XXX XXXX"
          className="rounded-l-none"
          {...register('phone')}
        />
      </div>
      <FormFieldError fieldName="phone" />
    </div>
  );
};
