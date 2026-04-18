'use client';

import { useState } from 'react';
import { useStoreCheckoutStore } from '@/stores/store';
import { CheckoutGuard, BackButton, ContinueButton } from '../CheckoutLayout';
import { PaymentMethods } from './PaymentMethods';

export const PaymentStep = () => {
  const paymentMethod = useStoreCheckoutStore((s) => s.paymentMethod);
  const [error, setError] = useState<string | null>(null);

  const handleContinue = async (): Promise<boolean> => {
    if (!paymentMethod) {
      setError('Please select a payment method');
      return false;
    }
    setError(null);
    return true;
  };

  return (
    <CheckoutGuard>
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Select Payment Method</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Choose how you&apos;d like to pay for your order.
          </p>
        </div>

        <PaymentMethods />

        {error && <p className="text-sm text-red-600">{error}</p>}

        <div className="flex items-center justify-between pt-2">
          <BackButton />
          <ContinueButton onClick={handleContinue} label="Continue to Review" />
        </div>
      </div>
    </CheckoutGuard>
  );
};
