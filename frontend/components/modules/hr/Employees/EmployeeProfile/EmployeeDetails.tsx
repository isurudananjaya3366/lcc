'use client';

import { useEmployee, useTerminateEmployee, useReactivateEmployee } from '@/hooks/hr/useEmployees';
import { EmployeeProfileHeader } from './EmployeeProfileHeader';
import { EmployeeTabs } from './EmployeeTabs';
import { AlertTriangle } from 'lucide-react';

interface EmployeeDetailsProps {
  employeeId: string;
}

export function EmployeeDetails({ employeeId }: EmployeeDetailsProps) {
  const { data, isLoading, error } = useEmployee(employeeId);
  const terminateMutation = useTerminateEmployee();
  const reactivateMutation = useReactivateEmployee();

  if (isLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (error || !data?.data) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <AlertTriangle className="h-12 w-12 text-destructive" />
        <h2 className="text-lg font-semibold">Employee not found</h2>
        <p className="text-sm text-muted-foreground">
          {error?.message ?? 'The requested employee record could not be loaded.'}
        </p>
      </div>
    );
  }

  const employee = data.data;

  const handleTerminate = () => {
    const reason = window.prompt('Enter termination reason:');
    if (reason) {
      terminateMutation.mutate({
        id: employeeId,
        data: { date: new Date().toISOString().split('T')[0]!, reason },
      });
    }
  };

  const handleReactivate = () => {
    if (window.confirm('Are you sure you want to reactivate this employee?')) {
      reactivateMutation.mutate(employeeId);
    }
  };

  return (
    <div className="space-y-6">
      <EmployeeProfileHeader
        employee={employee}
        onTerminate={handleTerminate}
        onReactivate={handleReactivate}
      />
      <EmployeeTabs employee={employee} />
    </div>
  );
}
