'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Briefcase, DollarSign, Shield } from 'lucide-react';
import type { Employee } from '@/types/hr';

interface EmploymentInfoTabProps {
  employee: Employee;
}

function InfoRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="grid grid-cols-3 gap-4 py-2">
      <span className="text-sm font-medium text-muted-foreground">{label}</span>
      <span className="col-span-2 text-sm">{value || '—'}</span>
    </div>
  );
}

function formatCurrency(amount?: number): string {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

function calculateDuration(hireDate: string): string {
  const start = new Date(hireDate);
  const now = new Date();
  const years = now.getFullYear() - start.getFullYear();
  const months = now.getMonth() - start.getMonth();
  const totalMonths = years * 12 + months;
  const y = Math.floor(totalMonths / 12);
  const m = totalMonths % 12;
  if (y === 0) return `${m} month${m !== 1 ? 's' : ''}`;
  return `${y} year${y !== 1 ? 's' : ''}, ${m} month${m !== 1 ? 's' : ''}`;
}

export function EmploymentInfoTab({ employee }: EmploymentInfoTabProps) {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Briefcase className="h-4 w-4" />
            Position Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Department" value={employee.departmentId} />
          <Separator />
          <InfoRow label="Position" value={employee.positionId} />
          <Separator />
          <InfoRow label="Reports To" value={employee.managerId ?? '—'} />
          <Separator />
          <InfoRow label="Work Location" value={employee.workLocation} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Briefcase className="h-4 w-4" />
            Employment Status
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <div className="grid grid-cols-3 gap-4 py-2">
            <span className="text-sm font-medium text-muted-foreground">Employment Type</span>
            <span className="col-span-2">
              <Badge variant="outline">{employee.employmentType.replace('_', ' ')}</Badge>
            </span>
          </div>
          <Separator />
          <InfoRow
            label="Start Date"
            value={new Date(employee.hireDate).toLocaleDateString('en-LK')}
          />
          <Separator />
          <InfoRow label="Duration" value={calculateDuration(employee.hireDate)} />
          <Separator />
          <InfoRow
            label="Probation End"
            value={
              employee.probationEndDate
                ? new Date(employee.probationEndDate).toLocaleDateString('en-LK')
                : '—'
            }
          />
          {employee.terminationDate && (
            <>
              <Separator />
              <InfoRow
                label="Termination Date"
                value={new Date(employee.terminationDate).toLocaleDateString('en-LK')}
              />
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <DollarSign className="h-4 w-4" />
            Compensation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Basic Salary" value={formatCurrency(employee.salary)} />
          <Separator />
          <InfoRow label="Pay Schedule" value={employee.payrollSchedule} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Shield className="h-4 w-4" />
            Statutory Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Tax ID (TIN)" value={employee.taxId} />
          <Separator />
          <InfoRow label="SSN / EPF No." value={employee.socialSecurityNumber} />
        </CardContent>
      </Card>
    </div>
  );
}
