import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { RolesPage } from '@/components/modules/settings/Roles';

export const metadata = createSettingsMetadata(
  'Roles & Permissions',
  'Manage roles and permission-based access control for your organization.'
);

export default function RolesManagementPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <RolesPage />
    </Suspense>
  );
}
