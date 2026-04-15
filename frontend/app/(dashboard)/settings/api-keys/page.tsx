import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { APIKeysPage } from '@/components/modules/settings/APIKeys';

export const metadata = createSettingsMetadata(
  'API Keys',
  'Generate and manage API access keys for programmatic access to the system.'
);

export default function APIKeysManagementPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <APIKeysPage />
    </Suspense>
  );
}
