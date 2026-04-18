'use client';

import { useEffect, useRef } from 'react';
import { useStoreCheckoutStore, useStoreCartStore } from '@/stores/store';
import { SuccessAnimation } from './SuccessAnimation';
import { OrderNumber } from './OrderNumber';
import { WhatsAppConfirm } from './WhatsAppConfirm';
import { ContinueShopping } from './ContinueShopping';

export const ConfirmationStep = () => {
  const orderInfo = useStoreCheckoutStore((s) => s.orderInfo);
  const contactInfo = useStoreCheckoutStore((s) => s.contactInfo);
  const clearCartAfterCheckout = useStoreCartStore((s) => s.clearCartAfterCheckout);
  const resetCheckout = useStoreCheckoutStore((s) => s.reset);
  const cleanedUp = useRef(false);

  useEffect(() => {
    if (!cleanedUp.current) {
      cleanedUp.current = true;
      clearCartAfterCheckout();
      resetCheckout();
    }
  }, [clearCartAfterCheckout, resetCheckout]);

  const orderNumber = orderInfo?.orderNumber ?? 'LCC-0000-00000';
  const whatsappOptIn = contactInfo.whatsappOptIn;
  const phone = contactInfo.phone;

  return (
    <div className="mx-auto max-w-lg space-y-8 py-8 text-center">
      <SuccessAnimation />

      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-gray-900">Thank you for your order!</h1>
        <p className="text-sm text-gray-500">
          We&apos;ve received your order and will begin processing it shortly.
        </p>
      </div>

      <OrderNumber orderNumber={orderNumber} />

      <div className="space-y-4 text-left">
        <div className="rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
          <p>
            A confirmation email has been sent to your email address. You can use the order number
            above to track your order status.
          </p>
        </div>

        {whatsappOptIn && phone && <WhatsAppConfirm phone={phone} />}
      </div>

      <ContinueShopping />
    </div>
  );
};
