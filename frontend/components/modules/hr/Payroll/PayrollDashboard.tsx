'use client';

import { PayrollHeader } from './PayrollHeader';
import { PayrollSummaryCards } from './PayrollSummaryCards';
import { PayrollPeriodsTable } from './PayrollPeriodsTable';
import { usePayrollRuns } from '@/hooks/hr/usePayroll';
import { Skeleton } from '@/components/ui/skeleton';

export function PayrollDashboard() {
  const { data, isLoading } = usePayrollRuns();
  const payrolls = data?.data ?? [];

  return (
    <div className="space-y-6">
      <PayrollHeader />

      {isLoading ? (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
          <Skeleton className="h-64" />
        </>
      ) : (
        <>
          <PayrollSummaryCards payrolls={payrolls} />
          <PayrollPeriodsTable payrolls={payrolls} />
        </>
      )}
    </div>
  );
}
