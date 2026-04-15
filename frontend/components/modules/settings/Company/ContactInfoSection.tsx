'use client';

import { UseFormReturn } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { SettingsSectionCard } from '../General/SettingsSectionCard';
import type { CompanyFormValues } from '@/lib/validations/company';

interface ContactInfoSectionProps {
  form: UseFormReturn<CompanyFormValues>;
}

export function ContactInfoSection({ form }: ContactInfoSectionProps) {
  return (
    <SettingsSectionCard title="Contact Information" description="Company contact details">
      <div className="grid gap-4 sm:grid-cols-2">
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone</FormLabel>
              <FormControl>
                <Input placeholder="+94XXXXXXXXX" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="company@example.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name="website"
        render={({ field }) => (
          <FormItem className="mt-4">
            <FormLabel>Website</FormLabel>
            <FormControl>
              <Input placeholder="https://www.example.com" {...field} value={field.value ?? ''} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </SettingsSectionCard>
  );
}
