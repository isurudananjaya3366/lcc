import { Suspense } from 'react';
import { createSettingsMetadata } from '@/lib/metadata/settings';
import { AuditLogPage } from '@/components/modules/settings/AuditLog';

export const metadata = createSettingsMetadata(
  'Audit Log',
  'View system activity, user actions, and security events audit trail.'
);

export default function AuditLogManagementPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <AuditLogPage />
    </Suspense>
  );
}
