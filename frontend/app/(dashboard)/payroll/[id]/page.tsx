import { Suspense } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { createHRMetadata } from '@/lib/metadata/hr';
import { PayslipDetails } from '@/components/modules/hr/Payroll';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return createHRMetadata(
    `Payslip ${id}`,
    'View payslip details including earnings, deductions, EPF/ETF contributions, and net pay.'
  );
}

export default async function PayslipDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <Suspense
      fallback={
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      }
    >
      <PayslipDetails payrollId={id} />
    </Suspense>
  );
}
