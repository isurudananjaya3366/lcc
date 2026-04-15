'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, CheckCircle } from 'lucide-react';

interface ConfirmProcessingStepProps {
  month: number;
  year: number;
  employeeCount: number;
  onConfirm: () => void;
  isPending: boolean;
}

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

export function ConfirmProcessingStep({
  month,
  year,
  employeeCount,
  onConfirm,
  isPending,
}: ConfirmProcessingStepProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Confirm & Process</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-start gap-3 rounded-md border border-yellow-300 bg-yellow-50 p-4 dark:border-yellow-600 dark:bg-yellow-900/20">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-yellow-600" />
          <div>
            <p className="font-medium text-yellow-800 dark:text-yellow-400">
              Please review before processing
            </p>
            <p className="mt-1 text-sm text-yellow-700 dark:text-yellow-500">
              Once processed, payroll calculations cannot be undone. Ensure all employee selections
              and calculations are correct.
            </p>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between border-b pb-2">
            <span className="text-muted-foreground">Period</span>
            <span className="font-medium">
              {MONTHS[month - 1]} {year}
            </span>
          </div>
          <div className="flex items-center justify-between border-b pb-2">
            <span className="text-muted-foreground">Employees</span>
            <span className="font-medium">{employeeCount}</span>
          </div>
        </div>

        <Button
          onClick={onConfirm}
          disabled={isPending || employeeCount === 0}
          className="w-full"
          size="lg"
        >
          {isPending ? (
            'Processing...'
          ) : (
            <>
              <CheckCircle className="mr-2 h-4 w-4" />
              Confirm & Process Payroll
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
