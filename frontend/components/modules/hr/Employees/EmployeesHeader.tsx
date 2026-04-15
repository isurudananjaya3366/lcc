'use client';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';

export function EmployeesHeader() {
  const router = useRouter();

  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Employees</h1>
        <p className="text-muted-foreground">Manage your workforce and employee records</p>
      </div>
      <Button onClick={() => router.push('/employees/new')}>
        <Plus className="mr-2 h-4 w-4" />
        Add Employee
      </Button>
    </div>
  );
}
