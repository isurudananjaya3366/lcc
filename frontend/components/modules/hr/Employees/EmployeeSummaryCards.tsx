'use client';

import { Card, CardContent } from '@/components/ui/card';
import { Users, UserCheck, Building2 } from 'lucide-react';
import type { Employee, Department } from '@/types/hr';

interface EmployeeSummaryCardsProps {
  employees: Employee[];
  departments: Department[];
}

export function EmployeeSummaryCards({ employees, departments }: EmployeeSummaryCardsProps) {
  const totalEmployees = employees.length;
  const activeEmployees = employees.filter((e) => e.status === 'ACTIVE').length;
  const totalDepartments = departments.length;

  const cards = [
    {
      title: 'Total Employees',
      value: totalEmployees,
      icon: Users,
      iconColor: 'text-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-950',
    },
    {
      title: 'Active Employees',
      value: activeEmployees,
      icon: UserCheck,
      iconColor: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-950',
    },
    {
      title: 'Departments',
      value: totalDepartments,
      icon: Building2,
      iconColor: 'text-purple-500',
      bgColor: 'bg-purple-50 dark:bg-purple-950',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardContent className="flex items-center gap-4 p-6">
            <div className={`rounded-lg p-3 ${card.bgColor}`}>
              <card.icon className={`h-6 w-6 ${card.iconColor}`} />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{card.title}</p>
              <p className="text-2xl font-bold">{card.value}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
