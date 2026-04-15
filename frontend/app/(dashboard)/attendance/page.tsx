import { Suspense } from 'react';
import { createHRMetadata } from '@/lib/metadata/hr';
import { AttendanceDashboard } from '@/components/modules/hr';

export const metadata = createHRMetadata(
  'Attendance',
  'Track daily attendance, view check-in/out records, and manage attendance across departments.'
);

export default function AttendancePage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <AttendanceDashboard />
    </Suspense>
  );
}
