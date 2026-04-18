'use client';

import { StepProgress } from '@/components/storefront/checkout';
import { ShippingStep } from '@/components/storefront/checkout';

export default function ShippingPage() {
  return (
    <>
      <StepProgress />
      <div className="mt-6">
        <ShippingStep />
      </div>
    </>
  );
}
