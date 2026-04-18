'use client';

import { StepProgress } from '@/components/storefront/checkout';
import { PaymentStep } from '@/components/storefront/checkout/Payment';

export default function PaymentPage() {
  return (
    <>
      <StepProgress />
      <div className="mt-6">
        <PaymentStep />
      </div>
    </>
  );
}
