'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { PayslipHeader } from './PayslipHeader';
import { PayslipEarnings } from './PayslipEarnings';
import { PayslipDeductions } from './PayslipDeductions';
import { PayslipPDF } from './PayslipPDF';
import { usePayrollById, usePayrollItems } from '@/hooks/hr/usePayroll';
import { Skeleton } from '@/components/ui/skeleton';

interface PayslipDetailsProps {
  payrollId: string;
}

export function PayslipDetails({ payrollId }: PayslipDetailsProps) {
  const router = useRouter();
  const { data: payrollData, isLoading: loadingPayroll } = usePayrollById(payrollId);
  const { data: itemsData, isLoading: loadingItems } = usePayrollItems(payrollId);

  const payroll = payrollData?.data;
  const items = itemsData?.data ?? [];

  if (loadingPayroll || loadingItems) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-32" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (!payroll) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        <p className="text-muted-foreground">Payroll not found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-2xl font-bold tracking-tight">Payslip Details</h1>
        </div>
      </div>

      <PayslipHeader payroll={payroll} />

      {items.length > 0 ? (
        items.map((item) => (
          <div key={item.id} className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Employee: {item.employeeId}</h3>
              <PayslipPDF payrollId={payrollId} employeeId={item.employeeId} />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <PayslipEarnings item={item} />
              <PayslipDeductions item={item} />
            </div>
          </div>
        ))
      ) : (
        <p className="text-center text-muted-foreground">No payroll items found for this period.</p>
      )}
    </div>
  );
}
