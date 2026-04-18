'use client';

import { useFormContext } from 'react-hook-form';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';

export const WhatsAppCheckbox = () => {
  const { setValue, watch } = useFormContext();
  const checked = watch('whatsappOptIn');

  return (
    <div className="flex items-center space-x-2">
      <Checkbox
        id="whatsappOptIn"
        checked={checked}
        onCheckedChange={(value) => setValue('whatsappOptIn', Boolean(value))}
      />
      <Label htmlFor="whatsappOptIn" className="text-sm font-normal cursor-pointer">
        Send order updates via WhatsApp
      </Label>
    </div>
  );
};
