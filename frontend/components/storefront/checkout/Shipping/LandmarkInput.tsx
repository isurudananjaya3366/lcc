'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FormFieldError } from '../Information/FormFieldError';

export const LandmarkInput = () => {
  const { register } = useFormContext();

  return (
    <div className="space-y-2">
      <Label htmlFor="landmark">Nearby Landmark</Label>
      <Input
        id="landmark"
        type="text"
        placeholder="e.g., Near the town mosque"
        {...register('landmark')}
      />
      <p className="text-xs text-muted-foreground">e.g., Near the town mosque</p>
      <FormFieldError fieldName="landmark" />
    </div>
  );
};
