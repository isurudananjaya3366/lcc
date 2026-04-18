'use client';

import { useEffect } from 'react';
import { type UseFormReturn } from 'react-hook-form';
import { useStoreCheckoutStore } from '@/stores/store';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function usePreFillInfo(form: UseFormReturn<any>) {
  const contactInfo = useStoreCheckoutStore((s) => s.contactInfo);

  useEffect(() => {
    const { email, phone, firstName, lastName, whatsappOptIn } = contactInfo;

    if (email || phone || firstName || lastName) {
      form.reset(
        {
          email: email || '',
          phone: phone || '',
          firstName: firstName || '',
          lastName: lastName || '',
          whatsappOptIn,
        },
        { keepDefaultValues: false }
      );
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
}
