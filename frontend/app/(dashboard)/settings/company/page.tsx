import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { CompanySettings } from '@/components/modules/settings/Company';

export const metadata = createSettingsMetadata(
  'Company Settings',
  'Configure your company profile, logo, address, tax information, and contact details.'
);

export default function CompanySettingsPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <CompanySettings />
    </Suspense>
  );
}
