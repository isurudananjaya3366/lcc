'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { PayrollItem } from '@/types/hr';

interface PayslipDeductionsProps {
  item: PayrollItem;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function PayslipDeductions({ item }: PayslipDeductionsProps) {
  const epfEmployee = item.deductions.find((d) => d.name === 'EPF Employee');
  const epfEmployer = item.deductions.find((d) => d.name === 'EPF Employer');
  const etf = item.deductions.find((d) => d.name === 'ETF');
  const otherDeductions = item.deductions.filter(
    (d) => !['EPF Employee', 'EPF Employer', 'ETF'].includes(d.name)
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Deductions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Description</TableHead>
              <TableHead className="text-right">Amount (LKR)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {epfEmployee && (
              <TableRow>
                <TableCell>EPF Employee (8%)</TableCell>
                <TableCell className="text-right">{formatLKR(epfEmployee.amount)}</TableCell>
              </TableRow>
            )}
            {epfEmployer && (
              <TableRow>
                <TableCell>EPF Employer (12%)</TableCell>
                <TableCell className="text-right">{formatLKR(epfEmployer.amount)}</TableCell>
              </TableRow>
            )}
            {etf && (
              <TableRow>
                <TableCell>ETF (3%)</TableCell>
                <TableCell className="text-right">{formatLKR(etf.amount)}</TableCell>
              </TableRow>
            )}
            {item.taxAmount > 0 && (
              <TableRow>
                <TableCell>PAYE Tax</TableCell>
                <TableCell className="text-right">{formatLKR(item.taxAmount)}</TableCell>
              </TableRow>
            )}
            {otherDeductions.map((d) => (
              <TableRow key={d.name}>
                <TableCell>{d.name}</TableCell>
                <TableCell className="text-right">{formatLKR(d.amount)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="flex items-center justify-between rounded-md bg-green-50 p-4 dark:bg-green-900/20">
          <span className="text-lg font-bold">Net Pay</span>
          <span className="text-lg font-bold text-green-700 dark:text-green-400">
            {formatLKR(item.netPay)}
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
