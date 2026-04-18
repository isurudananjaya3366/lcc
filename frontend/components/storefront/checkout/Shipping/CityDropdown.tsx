'use client';

import { useFormContext, useWatch } from 'react-hook-form';
import { Label } from '@/components/ui/label';
import { citiesByDistrict } from '@/data/srilanka';
import { FormFieldError } from '../Information/FormFieldError';
import type { ShippingStepData } from '@/lib/validations/checkoutSchemas';

export const CityDropdown = () => {
  const { register } = useFormContext<ShippingStepData>();
  const district = useWatch<ShippingStepData>({ name: 'district' });

  const cities = district ? (citiesByDistrict[district] ?? []) : [];

  return (
    <div className="space-y-2">
      <Label htmlFor="city">
        City <span className="text-red-500">*</span>
      </Label>
      <select
        id="city"
        {...register('city')}
        disabled={!district}
        className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <option value="">Select city</option>
        {cities.map((city) => (
          <option key={city} value={city}>
            {city}
          </option>
        ))}
      </select>
      <FormFieldError fieldName="city" />
    </div>
  );
};
