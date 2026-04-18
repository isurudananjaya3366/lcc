'use client';

import { useFormContext, useWatch } from 'react-hook-form';
import { Label } from '@/components/ui/label';
import { districtsByProvince } from '@/data/srilanka';
import { FormFieldError } from '../Information/FormFieldError';
import type { ShippingStepData } from '@/lib/validations/checkoutSchemas';

export const DistrictDropdown = () => {
  const { register, setValue } = useFormContext<ShippingStepData>();
  const province = useWatch<ShippingStepData>({ name: 'province' });

  const districts = province ? (districtsByProvince[province] ?? []) : [];

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    setValue('district', value, { shouldValidate: true });
    setValue('city', '', { shouldValidate: false });
  };

  return (
    <div className="space-y-2">
      <Label htmlFor="district">
        District <span className="text-red-500">*</span>
      </Label>
      <select
        id="district"
        {...register('district')}
        onChange={handleChange}
        disabled={!province}
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <option value="">Select district</option>
        {districts.map((d) => (
          <option key={d.code} value={d.code}>
            {d.name}
          </option>
        ))}
      </select>
      <FormFieldError fieldName="district" />
    </div>
  );
};
