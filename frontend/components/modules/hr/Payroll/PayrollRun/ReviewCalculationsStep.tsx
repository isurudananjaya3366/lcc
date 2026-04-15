'use client';

import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { Employee } from '@/types/hr';

interface ReviewCalculationsStepProps {
  employees: Employee[];
  selectedIds: string[];
}

interface CalculatedPayroll {
  employeeId: string;
  name: string;
  basicSalary: number;
  epfEmployee: number;
  epfEmployer: number;
  etf: number;
  paye: number;
  grossPay: number;
  totalDeductions: number;
  netPay: number;
}

const EPF_EMPLOYEE_RATE = 0.08;
const EPF_EMPLOYER_RATE = 0.12;
const ETF_RATE = 0.03;

function calculatePAYE(annualIncome: number): number {
  // Sri Lanka PAYE tax slabs (simplified)
  const monthly = annualIncome / 12;
  if (monthly <= 100000) return 0;
  if (monthly <= 141667) return (monthly - 100000) * 0.06;
  if (monthly <= 183333) return 2500 + (monthly - 141667) * 0.12;
  if (monthly <= 225000) return 7500 + (monthly - 183333) * 0.18;
  if (monthly <= 266667) return 15000 + (monthly - 225000) * 0.24;
  if (monthly <= 308333) return 25000 + (monthly - 266667) * 0.3;
  return 37500 + (monthly - 308333) * 0.36;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function ReviewCalculationsStep({ employees, selectedIds }: ReviewCalculationsStepProps) {
  const calculations = useMemo<CalculatedPayroll[]>(() => {
    return employees
      .filter((e) => selectedIds.includes(e.id))
      .map((e) => {
        const basic = e.salary ?? 0;
        const epfEmp = basic * EPF_EMPLOYEE_RATE;
        const epfEr = basic * EPF_EMPLOYER_RATE;
        const etf = basic * ETF_RATE;
        const paye = calculatePAYE(basic * 12);
        const totalDeductions = epfEmp + paye;
        const grossPay = basic;
        const netPay = grossPay - totalDeductions;

        return {
          employeeId: e.id,
          name: `${e.firstName} ${e.lastName}`,
          basicSalary: basic,
          epfEmployee: epfEmp,
          epfEmployer: epfEr,
          etf,
          paye,
          grossPay,
          totalDeductions,
          netPay,
        };
      });
  }, [employees, selectedIds]);

  const totals = useMemo(() => {
    return calculations.reduce(
      (acc, c) => ({
        gross: acc.gross + c.grossPay,
        epfEmployee: acc.epfEmployee + c.epfEmployee,
        epfEmployer: acc.epfEmployer + c.epfEmployer,
        etf: acc.etf + c.etf,
        paye: acc.paye + c.paye,
        deductions: acc.deductions + c.totalDeductions,
        net: acc.net + c.netPay,
      }),
      { gross: 0, epfEmployee: 0, epfEmployer: 0, etf: 0, paye: 0, deductions: 0, net: 0 }
    );
  }, [calculations]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Review Calculations</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-4">
          <div className="rounded-md bg-muted p-3">
            <p className="text-xs text-muted-foreground">Gross Pay</p>
            <p className="text-lg font-bold">{formatLKR(totals.gross)}</p>
          </div>
          <div className="rounded-md bg-muted p-3">
            <p className="text-xs text-muted-foreground">EPF (Employee 8%)</p>
            <p className="text-lg font-bold">{formatLKR(totals.epfEmployee)}</p>
          </div>
          <div className="rounded-md bg-muted p-3">
            <p className="text-xs text-muted-foreground">EPF (Employer 12%) + ETF (3%)</p>
            <p className="text-lg font-bold">{formatLKR(totals.epfEmployer + totals.etf)}</p>
          </div>
          <div className="rounded-md bg-green-50 p-3 dark:bg-green-900/20">
            <p className="text-xs text-muted-foreground">Net Pay</p>
            <p className="text-lg font-bold text-green-700 dark:text-green-400">
              {formatLKR(totals.net)}
            </p>
          </div>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead className="text-right">Basic</TableHead>
                <TableHead className="text-right">EPF (8%)</TableHead>
                <TableHead className="text-right">PAYE</TableHead>
                <TableHead className="text-right">Deductions</TableHead>
                <TableHead className="text-right">Net Pay</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {calculations.map((calc) => (
                <TableRow key={calc.employeeId}>
                  <TableCell className="font-medium">{calc.name}</TableCell>
                  <TableCell className="text-right">{formatLKR(calc.basicSalary)}</TableCell>
                  <TableCell className="text-right">{formatLKR(calc.epfEmployee)}</TableCell>
                  <TableCell className="text-right">{formatLKR(calc.paye)}</TableCell>
                  <TableCell className="text-right">{formatLKR(calc.totalDeductions)}</TableCell>
                  <TableCell className="text-right font-medium">{formatLKR(calc.netPay)}</TableCell>
                </TableRow>
              ))}
              <TableRow className="bg-muted/50 font-bold">
                <TableCell>Total</TableCell>
                <TableCell className="text-right">{formatLKR(totals.gross)}</TableCell>
                <TableCell className="text-right">{formatLKR(totals.epfEmployee)}</TableCell>
                <TableCell className="text-right">{formatLKR(totals.paye)}</TableCell>
                <TableCell className="text-right">{formatLKR(totals.deductions)}</TableCell>
                <TableCell className="text-right">{formatLKR(totals.net)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
