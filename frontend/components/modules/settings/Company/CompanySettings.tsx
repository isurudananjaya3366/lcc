'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Save } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { companyFormSchema, type CompanyFormValues } from '@/lib/validations/company';
import { SettingsSectionCard } from '../General/SettingsSectionCard';
import { LogoUpload } from './LogoUpload';
import { CompanyNameInput } from './CompanyNameInput';
import { CompanyAddressForm } from './CompanyAddressForm';
import { TaxInfoSection } from './TaxInfoSection';
import { ContactInfoSection } from './ContactInfoSection';

const defaultValues: CompanyFormValues = {
  name: '',
  logo: '',
  address: {
    street: '',
    city: '',
    province: '',
    postalCode: '',
    country: 'Sri Lanka',
  },
  tin: '',
  vatNumber: '',
  taxRegistrationType: '',
  phone: '',
  email: '',
  website: '',
};

export function CompanySettings() {
  const [isSaving, setIsSaving] = useState(false);

  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companyFormSchema),
    defaultValues,
  });

  const { isDirty } = form.formState;

  const onSubmit = async (data: CompanyFormValues) => {
    setIsSaving(true);
    try {
      // In production: POST/PUT /api/settings/company
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log('Company settings saved:', data);
      form.reset(data);
    } catch {
      console.error('Failed to save company settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Company Settings</h2>
        <p className="text-muted-foreground">
          Manage your company profile, address, and tax information
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <SettingsSectionCard title="Company Logo" description="Upload your company logo">
            <LogoUpload
              value={form.watch('logo')}
              onChange={(value) => form.setValue('logo', value, { shouldDirty: true })}
              onRemove={() => form.setValue('logo', '', { shouldDirty: true })}
            />
          </SettingsSectionCard>

          <CompanyNameInput form={form} />
          <CompanyAddressForm form={form} />
          <TaxInfoSection form={form} />
          <ContactInfoSection form={form} />

          <div className="flex justify-end">
            <Button type="submit" disabled={!isDirty || isSaving}>
              {isSaving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
