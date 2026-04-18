'use client';

import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useStoreCheckoutStore } from '@/stores/store';
import { useCheckoutNavigation } from '@/hooks/storefront/useCheckoutNavigation';
import { shippingStepSchema, type ShippingStepData } from '@/lib/validations/checkoutSchemas';
import { CheckoutGuard } from '../CheckoutLayout';
import { BackButton, ContinueButton } from '../CheckoutLayout';
import { AddressSection } from './AddressSection';
import { ShippingMethods } from './ShippingMethods';
import { shippingMethods } from './ShippingMethods';

export const ShippingStep = () => {
  const setShippingAddress = useStoreCheckoutStore((s) => s.setShippingAddress);
  const setShippingMethod = useStoreCheckoutStore((s) => s.setShippingMethod);
  const shippingAddress = useStoreCheckoutStore((s) => s.shippingAddress);
  const storedMethod = useStoreCheckoutStore((s) => s.shippingMethod);
  const { goToNext } = useCheckoutNavigation();

  const form = useForm({
    resolver: zodResolver(shippingStepSchema),
    defaultValues: {
      province: shippingAddress.province || '',
      district: shippingAddress.district || '',
      city: shippingAddress.city || '',
      address1: shippingAddress.address1 || '',
      address2: shippingAddress.address2 || '',
      landmark: shippingAddress.landmark || '',
      postalCode: shippingAddress.postalCode || '',
      shippingMethodId: storedMethod?.id || '',
    },
  });

  const onSubmit = (data: Record<string, unknown>) => {
    const parsed = data as ShippingStepData;
    const { shippingMethodId, ...address } = parsed;

    setShippingAddress(address);

    const selectedMethod = shippingMethods.find((m) => m.id === shippingMethodId);
    if (selectedMethod) {
      setShippingMethod({
        id: selectedMethod.id,
        name: selectedMethod.name,
        description: selectedMethod.description,
        price: selectedMethod.price,
        estimatedDays: parseInt(selectedMethod.estimatedDays, 10) || 0,
        carrier: selectedMethod.icon === 'express' ? 'Express Courier' : 'Standard Courier',
      });
    }

    goToNext();
  };

  return (
    <CheckoutGuard>
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <AddressSection />
          <ShippingMethods />
          <div className="flex items-center justify-between">
            <BackButton />
            <ContinueButton
              onClick={async () => {
                const valid = await form.trigger();
                if (valid) {
                  form.handleSubmit(onSubmit)();
                }
                return false;
              }}
              label="Continue to Payment"
            />
          </div>
        </form>
      </FormProvider>
    </CheckoutGuard>
  );
};
