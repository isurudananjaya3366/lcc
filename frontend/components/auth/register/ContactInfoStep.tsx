'use client';

import type { UseFormReturn } from 'react-hook-form';

import { Input } from '@/components/ui/input';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { RegistrationFormData } from '@/lib/validations/register';

const TIMEZONES = [
  { value: 'Asia/Colombo', label: 'Asia/Colombo (GMT+5:30)' },
  { value: 'Asia/Kolkata', label: 'Asia/Kolkata (GMT+5:30)' },
  { value: 'Asia/Dubai', label: 'Asia/Dubai (GMT+4:00)' },
  { value: 'Asia/Singapore', label: 'Asia/Singapore (GMT+8:00)' },
  { value: 'Europe/London', label: 'Europe/London (GMT+0:00)' },
  { value: 'America/New_York', label: 'America/New York (GMT-5:00)' },
] as const;

interface ContactInfoStepProps {
  form: UseFormReturn<RegistrationFormData>;
  disabled?: boolean;
}

export function ContactInfoStep({ form, disabled }: ContactInfoStepProps) {
  return (
    <div className="space-y-4">
      <FormField
        control={form.control}
        name="phone"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Phone Number</FormLabel>
            <FormControl>
              <Input type="tel" placeholder="+94 77 123 4567" disabled={disabled} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="address.street"
        render={({ field }) => (
          <FormItem>
            <FormLabel>
              Street Address <span className="text-gray-400">(optional)</span>
            </FormLabel>
            <FormControl>
              <Input placeholder="123 Main Street" disabled={disabled} {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="grid grid-cols-2 gap-4">
        <FormField
          control={form.control}
          name="address.city"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                City <span className="text-gray-400">(optional)</span>
              </FormLabel>
              <FormControl>
                <Input placeholder="Colombo" disabled={disabled} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="address.postalCode"
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Postal Code <span className="text-gray-400">(optional)</span>
              </FormLabel>
              <FormControl>
                <Input placeholder="10100" disabled={disabled} {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name="timezone"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Timezone</FormLabel>
            <Select onValueChange={field.onChange} defaultValue={field.value} disabled={disabled}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select timezone" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {TIMEZONES.map((tz) => (
                  <SelectItem key={tz.value} value={tz.value}>
                    {tz.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
