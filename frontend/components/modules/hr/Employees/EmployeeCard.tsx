'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreVertical, Eye, Pencil, Trash2, Mail, Phone } from 'lucide-react';
import { EmployeeAvatar } from './EmployeeAvatar';
import type { Employee } from '@/types/hr';

interface EmployeeCardProps {
  employee: Employee;
  onDelete?: (id: string) => void;
}

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  ACTIVE: 'default',
  ON_LEAVE: 'secondary',
  SUSPENDED: 'destructive',
  TERMINATED: 'destructive',
  RETIRED: 'outline',
};

export function EmployeeCard({ employee, onDelete }: EmployeeCardProps) {
  const router = useRouter();

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <EmployeeAvatar firstName={employee.firstName} lastName={employee.lastName} size="lg" />
            <div>
              <h3 className="font-semibold">
                {employee.firstName} {employee.lastName}
              </h3>
              <p className="text-sm text-muted-foreground">{employee.employeeNumber}</p>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => router.push(`/employees/${employee.id}`)}>
                <Eye className="mr-2 h-4 w-4" />
                View Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => router.push(`/employees/${employee.id}?edit=true`)}>
                <Pencil className="mr-2 h-4 w-4" />
                Edit
              </DropdownMenuItem>
              {onDelete && (
                <DropdownMenuItem
                  className="text-destructive"
                  onClick={() => onDelete(employee.id)}
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="mt-4 space-y-2">
          <Badge variant={statusVariant[employee.status] ?? 'outline'}>
            {employee.status.replace('_', ' ')}
          </Badge>

          {employee.email && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Mail className="h-3.5 w-3.5" />
              <span className="truncate">{employee.email}</span>
            </div>
          )}
          {employee.phone && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Phone className="h-3.5 w-3.5" />
              <span>{employee.phone}</span>
            </div>
          )}
        </div>

        <div className="mt-4">
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => router.push(`/employees/${employee.id}`)}
          >
            View Profile
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
