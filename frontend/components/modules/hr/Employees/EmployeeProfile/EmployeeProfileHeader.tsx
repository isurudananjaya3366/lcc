'use client';

import { useRouter } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Pencil, UserMinus, UserPlus } from 'lucide-react';
import { EmployeeAvatar } from '../EmployeeAvatar';
import type { Employee } from '@/types/hr';

interface EmployeeProfileHeaderProps {
  employee: Employee;
  onTerminate?: () => void;
  onReactivate?: () => void;
}

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  ACTIVE: 'default',
  ON_LEAVE: 'secondary',
  SUSPENDED: 'destructive',
  TERMINATED: 'destructive',
  RETIRED: 'outline',
};

export function EmployeeProfileHeader({
  employee,
  onTerminate,
  onReactivate,
}: EmployeeProfileHeaderProps) {
  const router = useRouter();

  return (
    <div className="space-y-4">
      <Button variant="ghost" size="sm" onClick={() => router.push('/employees')}>
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Employees
      </Button>

      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <EmployeeAvatar firstName={employee.firstName} lastName={employee.lastName} size="lg" />
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">
                {employee.firstName} {employee.lastName}
              </h1>
              <Badge variant={statusVariant[employee.status] ?? 'outline'}>
                {employee.status.replace('_', ' ')}
              </Badge>
            </div>
            <p className="text-muted-foreground">{employee.employeeNumber}</p>
            <p className="text-sm text-muted-foreground">
              Joined{' '}
              {new Date(employee.hireDate).toLocaleDateString('en-LK', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => router.push(`/employees/${employee.id}?edit=true`)}
          >
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Button>
          {employee.status === 'ACTIVE' && onTerminate && (
            <Button variant="destructive" onClick={onTerminate}>
              <UserMinus className="mr-2 h-4 w-4" />
              Terminate
            </Button>
          )}
          {employee.status === 'TERMINATED' && onReactivate && (
            <Button variant="outline" onClick={onReactivate}>
              <UserPlus className="mr-2 h-4 w-4" />
              Reactivate
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
