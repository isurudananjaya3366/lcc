import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { IntegrationsPage } from '@/components/modules/settings/Integrations';

export const metadata = createSettingsMetadata(
  'Integrations',
  'Connect and manage third-party integrations for payment, communication, and business tools.'
);

export default function IntegrationsManagementPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <IntegrationsPage />
    </Suspense>
  );
}
