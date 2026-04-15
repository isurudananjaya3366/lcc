import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { GeneralSettings } from '@/components/modules/settings/General';

export const metadata = createSettingsMetadata(
  'General Settings',
  'Configure general application settings including localization, timezone, currency, and notifications.'
);

export default function GeneralSettingsPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <GeneralSettings />
    </Suspense>
  );
}
