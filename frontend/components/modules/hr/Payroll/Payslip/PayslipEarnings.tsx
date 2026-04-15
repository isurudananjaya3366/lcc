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

interface PayslipEarningsProps {
  item: PayrollItem;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function PayslipEarnings({ item }: PayslipEarningsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Earnings</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Description</TableHead>
              <TableHead className="text-right">Amount (LKR)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>Basic Salary</TableCell>
              <TableCell className="text-right">{formatLKR(item.basicSalary)}</TableCell>
            </TableRow>
            {item.allowances.map((a) => (
              <TableRow key={a.name}>
                <TableCell>{a.name}</TableCell>
                <TableCell className="text-right">{formatLKR(a.amount)}</TableCell>
              </TableRow>
            ))}
            <TableRow className="bg-muted/50 font-bold">
              <TableCell>Gross Pay</TableCell>
              <TableCell className="text-right">{formatLKR(item.grossPay)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
