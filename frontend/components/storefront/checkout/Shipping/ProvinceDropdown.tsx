'use client';

import { useFormContext } from 'react-hook-form';
import { Label } from '@/components/ui/label';
import { provinces } from '@/data/srilanka';
import { FormFieldError } from '../Information/FormFieldError';
import type { ShippingStepData } from '@/lib/validations/checkoutSchemas';

export const ProvinceDropdown = () => {
  const { register, setValue } = useFormContext<ShippingStepData>();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setValue('province', value, { shouldValidate: true });
    setValue('district', '', { shouldValidate: false });
    setValue('city', '', { shouldValidate: false });
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="province">
        Province <span className="text-red-500">*</span>
      </Label>
      <select
        id="province"
        {...register('province')}
        onChange={handleChange}
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <option value="">Select province</option>
        {provinces.map((p) => (
          <option key={p.code} value={p.code}>
            {p.name}
          </option>
        ))}
      </select>
      <FormFieldError fieldName="province" />
    </div>
  );
};
