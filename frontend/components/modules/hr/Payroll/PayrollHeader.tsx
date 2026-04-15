'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export function PayrollHeader() {
  const router = useRouter();

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Payroll</h1>
        <p className="text-muted-foreground">
          Manage payroll runs, process salaries, and generate payslips
        </p>
      </div>
      <Button onClick={() => router.push('/payroll/run')}>
        <Plus className="mr-2 h-4 w-4" />
        Run Payroll
      </Button>
    </div>
  );
}
