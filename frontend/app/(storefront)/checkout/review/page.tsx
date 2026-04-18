'use client';

import { StepProgress } from '@/components/storefront/checkout';
import { ReviewStep } from '@/components/storefront/checkout/Review';

export default function ReviewPage() {
  return (
    <>
      <StepProgress />
      <div className="mt-6">
        <ReviewStep />
      </div>
    </>
  );
}
