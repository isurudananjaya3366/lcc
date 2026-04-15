import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { BillingPage } from '@/components/modules/settings/Billing';

export const metadata = createSettingsMetadata(
  'Billing & Plans',
  'Manage your subscription plan, billing history, and payment methods.'
);

export default function BillingManagementPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <BillingPage />
    </Suspense>
  );
}
