'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useDepartments, usePositions, useEmployees } from '@/hooks/hr/useEmployees';
import { EmploymentType } from '@/types/hr';
import type { UseFormRegister, FieldErrors, UseFormSetValue } from 'react-hook-form';
import type { EmployeeFormValues } from '@/lib/validations/employee';

interface EmploymentInfoSectionProps {
  register: UseFormRegister<EmployeeFormValues>;
  errors: FieldErrors<EmployeeFormValues>;
  setValue: UseFormSetValue<EmployeeFormValues>;
  employmentType?: EmploymentType;
  departmentId?: string;
  positionId?: string;
  managerId?: string;
}

const employmentTypeLabels: Record<string, string> = {
  [EmploymentType.FULL_TIME]: 'Full Time',
  [EmploymentType.PART_TIME]: 'Part Time',
  [EmploymentType.CONTRACT]: 'Contract',
  [EmploymentType.TEMPORARY]: 'Temporary',
  [EmploymentType.INTERN]: 'Intern',
};

export function EmploymentInfoSection({
  register,
  errors,
  setValue,
  employmentType,
  departmentId,
  positionId,
  managerId,
}: EmploymentInfoSectionProps) {
  const { data: deptData } = useDepartments();
  const { data: posData } = usePositions();
  const { data: empData } = useEmployees({});
  const departments = deptData?.data ?? [];
  const positions = posData?.data ?? [];
  const employees = empData?.data ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Employment Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Employment Type *</Label>
            <Select
              value={employmentType ?? ''}
              onValueChange={(v) => setValue('employmentType', v as EmploymentType)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(employmentTypeLabels).map(([key, label]) => (
                  <SelectItem key={key} value={key}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.employmentType && (
              <p className="text-xs text-destructive">{errors.employmentType.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="hireDate">Hire Date *</Label>
            <Input id="hireDate" type="date" {...register('hireDate')} />
            {errors.hireDate && (
              <p className="text-xs text-destructive">{errors.hireDate.message}</p>
            )}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Department *</Label>
            <Select value={departmentId ?? ''} onValueChange={(v) => setValue('departmentId', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select department" />
              </SelectTrigger>
              <SelectContent>
                {departments.map((d) => (
                  <SelectItem key={d.id} value={d.id}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.departmentId && (
              <p className="text-xs text-destructive">{errors.departmentId.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label>Position *</Label>
            <Select value={positionId ?? ''} onValueChange={(v) => setValue('positionId', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select position" />
              </SelectTrigger>
              <SelectContent>
                {positions.map((p) => (
                  <SelectItem key={p.id} value={p.id}>
                    {p.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.positionId && (
              <p className="text-xs text-destructive">{errors.positionId.message}</p>
            )}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="salary">Salary (LKR)</Label>
            <Input
              id="salary"
              type="number"
              min={0}
              step={1000}
              {...register('salary', { valueAsNumber: true })}
            />
            {errors.salary && <p className="text-xs text-destructive">{errors.salary.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="probationEndDate">Probation End Date</Label>
            <Input id="probationEndDate" type="date" {...register('probationEndDate')} />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="workLocation">Work Location</Label>
            <Input id="workLocation" {...register('workLocation')} />
          </div>
          <div className="space-y-2">
            <Label>Manager / Reports To</Label>
            <Select
              value={managerId ?? ''}
              onValueChange={(v) => setValue('managerId', v === '__none__' ? '' : v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select manager" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__none__">None</SelectItem>
                {employees.map((e) => (
                  <SelectItem key={e.id} value={e.id}>
                    {e.firstName} {e.lastName} ({e.employeeNumber})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="mb-3 text-sm font-medium">Bank Details</h4>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="bankName">Bank Name</Label>
              <Input id="bankName" {...register('bankName')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="bankAccountNumber">Account Number</Label>
              <Input id="bankAccountNumber" {...register('bankAccountNumber')} />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
