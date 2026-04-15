import { Suspense } from 'react';
import { createHRMetadata } from '@/lib/metadata/hr';
import { PayrollDashboard } from '@/components/modules/hr/Payroll';

export const metadata = createHRMetadata(
  'Payroll',
  'Payroll processing dashboard — manage payroll runs, view salary calculations, and track EPF/ETF contributions.'
);

export default function PayrollPage() {
  return (
    <Suspense
      fallback={<div className="animate-pulse h-96 rounded bg-gray-200 dark:bg-gray-700" />}
    >
      <PayrollDashboard />
    </Suspense>
  );
}
