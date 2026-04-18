'use client';

import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useStoreCheckoutStore } from '@/stores/store';
import { useCheckoutNavigation } from '@/hooks/storefront/useCheckoutNavigation';
import { informationStepSchema, type InformationStepData } from '@/lib/validations/checkoutSchemas';
import { CheckoutGuard } from '../CheckoutLayout';
import { ContactSection } from './ContactSection';
import { PersonalInfoSection } from './PersonalInfoSection';
import { ContinueButton } from '../CheckoutLayout';
import { usePreFillInfo } from './usePreFillInfo';

export const InformationStep = () => {
  const setContactInfo = useStoreCheckoutStore((s) => s.setContactInfo);
  const contactInfo = useStoreCheckoutStore((s) => s.contactInfo);
  const { goToNext } = useCheckoutNavigation();

  const form = useForm({
    resolver: zodResolver(informationStepSchema),
    defaultValues: {
      email: contactInfo.email || '',
      phone: contactInfo.phone || '',
      firstName: contactInfo.firstName || '',
      lastName: contactInfo.lastName || '',
      whatsappOptIn: contactInfo.whatsappOptIn ?? true,
    },
  });

  usePreFillInfo(form);

  const onSubmit = (data: Record<string, unknown>) => {
    setContactInfo(data as InformationStepData);
    goToNext();
  };

  return (
    <CheckoutGuard>
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <ContactSection />
          <PersonalInfoSection />
          <div className="flex justify-end">
            <ContinueButton
              onClick={async () => {
                const valid = await form.trigger();
                if (valid) {
                  form.handleSubmit(onSubmit)();
                }
                return false;
              }}
              label="Continue to Shipping"
            />
          </div>
        </form>
      </FormProvider>
    </CheckoutGuard>
  );
};
