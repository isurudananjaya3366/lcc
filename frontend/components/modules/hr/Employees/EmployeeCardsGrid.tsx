'use client';

import { EmployeeCard } from './EmployeeCard';
import type { Employee } from '@/types/hr';

interface EmployeeCardsGridProps {
  employees: Employee[];
  onDelete?: (id: string) => void;
}

export function EmployeeCardsGrid({ employees, onDelete }: EmployeeCardsGridProps) {
  if (employees.length === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center text-muted-foreground">
        No employees found matching your criteria.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {employees.map((employee) => (
        <EmployeeCard key={employee.id} employee={employee} onDelete={onDelete} />
      ))}
    </div>
  );
}
