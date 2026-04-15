import { Suspense } from 'react';
import { createHRMetadata } from '@/lib/metadata/hr';
import { LeaveDashboard } from '@/components/modules/hr/Leave';

export const metadata = createHRMetadata(
  'Leave Management',
  'Manage leave requests, view leave balances, and handle approval workflows.'
);

export default function LeavePage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <LeaveDashboard />
    </Suspense>
  );
}
