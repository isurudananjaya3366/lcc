'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ArrowRight } from 'lucide-react';
import { PeriodSelectionStep } from './PeriodSelectionStep';
import { EmployeeSelectionStep } from './EmployeeSelectionStep';
import { ReviewCalculationsStep } from './ReviewCalculationsStep';
import { ConfirmProcessingStep } from './ConfirmProcessingStep';
import { useEmployees } from '@/hooks/hr/useEmployees';
import { useCreatePayrollRun, useProcessPayroll } from '@/hooks/hr/usePayroll';
import { EmployeeStatus } from '@/types/hr';

const STEPS = ['Period', 'Employees', 'Review', 'Confirm'] as const;

export function PayrollRunPage() {
  const router = useRouter();
  const now = new Date();
  const [step, setStep] = useState(0);
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const { data: employeesData } = useEmployees({
    status: EmployeeStatus.ACTIVE,
  });
  const employees = employeesData?.data ?? [];

  const createMutation = useCreatePayrollRun();
  const processMutation = useProcessPayroll();

  // Default: select all active employees
  useState(() => {
    if (employees.length > 0 && selectedIds.length === 0) {
      setSelectedIds(employees.map((e) => e.id));
    }
  });

  const handleConfirm = () => {
    createMutation.mutate(
      { month, year },
      {
        onSuccess: (res) => {
          const payrollId = res.data.id;
          processMutation.mutate(payrollId, {
            onSuccess: () => router.push('/payroll'),
          });
        },
      }
    );
  };

  const canNext = step === 0 || (step === 1 && selectedIds.length > 0) || step === 2;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Run Payroll</h1>
          <p className="text-muted-foreground">
            Step {step + 1} of {STEPS.length}: {STEPS[step]}
          </p>
        </div>
      </div>

      {/* Step indicators */}
      <div className="flex gap-2">
        {STEPS.map((label, i) => (
          <div
            key={label}
            className={`flex-1 rounded-full py-1 text-center text-xs font-medium transition-colors ${
              i <= step ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
            }`}
          >
            {label}
          </div>
        ))}
      </div>

      {/* Step content */}
      {step === 0 && (
        <PeriodSelectionStep
          month={month}
          year={year}
          onMonthChange={setMonth}
          onYearChange={setYear}
        />
      )}
      {step === 1 && (
        <EmployeeSelectionStep
          employees={employees}
          selectedIds={selectedIds}
          onSelectionChange={setSelectedIds}
        />
      )}
      {step === 2 && <ReviewCalculationsStep employees={employees} selectedIds={selectedIds} />}
      {step === 3 && (
        <ConfirmProcessingStep
          month={month}
          year={year}
          employeeCount={selectedIds.length}
          onConfirm={handleConfirm}
          isPending={createMutation.isPending || processMutation.isPending}
        />
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={() => setStep((s) => s - 1)} disabled={step === 0}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
        {step < STEPS.length - 1 && (
          <Button onClick={() => setStep((s) => s + 1)} disabled={!canNext}>
            Next
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}
