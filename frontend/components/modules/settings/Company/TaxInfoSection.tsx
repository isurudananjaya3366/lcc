'use client';

import { UseFormReturn } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { SettingsSectionCard } from '../General/SettingsSectionCard';
import type { CompanyFormValues } from '@/lib/validations/company';

const TAX_REGISTRATION_TYPES = [
  { value: 'not_registered', label: 'Not Registered' },
  { value: 'vat_registered', label: 'VAT Registered' },
  { value: 'income_tax_only', label: 'Income Tax Only' },
  { value: 'both', label: 'Both' },
] as const;

interface TaxInfoSectionProps {
  form: UseFormReturn<CompanyFormValues>;
}

export function TaxInfoSection({ form }: TaxInfoSectionProps) {
  return (
    <SettingsSectionCard title="Tax Information" description="Tax registration details">
      <div className="grid gap-4 sm:grid-cols-2">
        <FormField
          control={form.control}
          name="tin"
          render={({ field }) => (
            <FormItem>
              <FormLabel>TIN (Tax Identification Number)</FormLabel>
              <FormControl>
                <Input placeholder="Enter TIN" {...field} value={field.value ?? ''} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="vatNumber"
          render={({ field }) => (
            <FormItem>
              <FormLabel>VAT Number</FormLabel>
              <FormControl>
                <Input placeholder="Enter VAT number" {...field} value={field.value ?? ''} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name="taxRegistrationType"
        render={({ field }) => (
          <FormItem className="mt-4">
            <FormLabel>Tax Registration Type</FormLabel>
            <Select onValueChange={field.onChange} value={field.value ?? ''}>
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select registration type" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {TAX_REGISTRATION_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />
    </SettingsSectionCard>
  );
}
