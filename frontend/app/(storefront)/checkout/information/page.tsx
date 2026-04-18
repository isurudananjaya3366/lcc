'use client';

import { StepProgress } from '@/components/storefront/checkout';
import { InformationStep } from '@/components/storefront/checkout';

export default function InformationPage() {
  return (
    <>
      <StepProgress />
      <div className="mt-6">
        <InformationStep />
      </div>
    </>
  );
}
