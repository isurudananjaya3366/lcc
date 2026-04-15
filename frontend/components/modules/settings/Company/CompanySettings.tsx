'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Save } from 'lucide-react';
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
  const form = useForm<CompanyFormValues>({
    resolver: zodResolver(companyFormSchema),
    defaultValues,
  });

  const onSubmit = (data: CompanyFormValues) => {
    // TODO: connect to API
    console.log('Company settings:', data);
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
              onChange={(value) => form.setValue('logo', value)}
              onRemove={() => form.setValue('logo', '')}
            />
          </SettingsSectionCard>

          <CompanyNameInput form={form} />
          <CompanyAddressForm form={form} />
          <TaxInfoSection form={form} />
          <ContactInfoSection form={form} />

          <div className="flex justify-end">
            <Button type="submit">
              <Save className="mr-2 h-4 w-4" />
              Save Changes
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}
