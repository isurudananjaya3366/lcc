'use client';

import { Card, CardContent } from '@/components/ui/card';
import { PeriodStatusBadge } from '../PeriodStatusBadge';
import type { Payroll } from '@/types/hr';

interface PayslipHeaderProps {
  payroll: Payroll;
}

export function PayslipHeader({ payroll }: PayslipHeaderProps) {
  return (
    <Card>
      <CardContent className="flex items-center justify-between p-6">
        <div>
          <h2 className="text-lg font-semibold">Payroll #{payroll.payrollNumber}</h2>
          <p className="text-sm text-muted-foreground">Period: {payroll.period}</p>
          {payroll.processedDate && (
            <p className="text-xs text-muted-foreground">
              Processed: {new Date(payroll.processedDate).toLocaleDateString()}
            </p>
          )}
        </div>
        <div className="text-right">
          <PeriodStatusBadge status={payroll.status} />
          <p className="mt-2 text-sm text-muted-foreground">{payroll.employeeCount} employees</p>
        </div>
      </CardContent>
    </Card>
  );
}
