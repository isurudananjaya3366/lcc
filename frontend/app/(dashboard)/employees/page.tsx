import { Suspense } from 'react';
import { createHRMetadata } from '@/lib/metadata/hr';
import { EmployeesList } from '@/components/modules/hr';

export const metadata = createHRMetadata(
  'Employees',
  'Employee directory — manage your workforce, view profiles, and track employee information.'
);

export default function EmployeesPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <EmployeesList />
    </Suspense>
  );
}
