'use client';

import { useRouter } from 'next/navigation';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Eye } from 'lucide-react';
import { PeriodStatusBadge } from './PeriodStatusBadge';
import type { Payroll } from '@/types/hr';

interface PayrollPeriodsTableProps {
  payrolls: Payroll[];
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function PayrollPeriodsTable({ payrolls }: PayrollPeriodsTableProps) {
  const router = useRouter();

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Period</TableHead>
            <TableHead className="text-center">Employees</TableHead>
            <TableHead className="text-right">Total (LKR)</TableHead>
            <TableHead className="text-center">Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {payrolls.length === 0 ? (
            <TableRow>
              <TableCell colSpan={5} className="h-32 text-center text-muted-foreground">
                No payroll runs found
              </TableCell>
            </TableRow>
          ) : (
            payrolls.map((payroll) => (
              <TableRow
                key={payroll.id}
                className="cursor-pointer"
                onClick={() => router.push(`/payroll/${payroll.id}`)}
              >
                <TableCell className="font-medium">{payroll.period}</TableCell>
                <TableCell className="text-center">{payroll.employeeCount}</TableCell>
                <TableCell className="text-right">{formatLKR(payroll.totalNet)}</TableCell>
                <TableCell className="text-center">
                  <PeriodStatusBadge status={payroll.status} />
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/payroll/${payroll.id}`);
                    }}
                  >
                    <Eye className="mr-1 h-4 w-4" />
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  );
}
