import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { UsersPage } from '@/components/modules/settings/Users';

export const metadata = createSettingsMetadata(
  'User Management',
  'Manage users, invitations, and access control for your organization.'
);

export default function UsersManagementPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <UsersPage />
    </Suspense>
  );
}
