'use client';

import { UseFormReturn } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { SettingsSectionCard } from '../General/SettingsSectionCard';
import type { CompanyFormValues } from '@/lib/validations/company';

interface CompanyNameInputProps {
  form: UseFormReturn<CompanyFormValues>;
}

export function CompanyNameInput({ form }: CompanyNameInputProps) {
  return (
    <SettingsSectionCard title="Company Name">
      <FormField
        control={form.control}
        name="name"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Company Name</FormLabel>
            <FormControl>
              <Input placeholder="Enter company name" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </SettingsSectionCard>
  );
}
