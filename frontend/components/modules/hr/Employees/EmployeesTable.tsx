'use client';

import { useRouter } from 'next/navigation';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal, Eye, Pencil, Trash2 } from 'lucide-react';
import { EmployeeAvatar } from './EmployeeAvatar';
import type { Employee } from '@/types/hr';

interface EmployeesTableProps {
  employees: Employee[];
  onDelete?: (id: string) => void;
}

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  ACTIVE: 'default',
  ON_LEAVE: 'secondary',
  SUSPENDED: 'destructive',
  TERMINATED: 'destructive',
  RETIRED: 'outline',
};

export function EmployeesTable({ employees, onDelete }: EmployeesTableProps) {
  const router = useRouter();

  if (employees.length === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center text-muted-foreground">
        No employees found matching your criteria.
      </div>
    );
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Employee</TableHead>
            <TableHead>Position</TableHead>
            <TableHead>Department</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Phone</TableHead>
            <TableHead>Email</TableHead>
            <TableHead>Join Date</TableHead>
            <TableHead className="w-[50px]" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {employees.map((employee) => (
            <TableRow
              key={employee.id}
              className="cursor-pointer"
              onClick={() => router.push(`/employees/${employee.id}`)}
            >
              <TableCell>
                <div className="flex items-center gap-3">
                  <EmployeeAvatar
                    firstName={employee.firstName}
                    lastName={employee.lastName}
                    size="sm"
                  />
                  <div>
                    <p className="font-medium">
                      {employee.firstName} {employee.lastName}
                    </p>
                    <p className="text-xs text-muted-foreground">{employee.employeeNumber}</p>
                  </div>
                </div>
              </TableCell>
              <TableCell>{employee.positionId}</TableCell>
              <TableCell>{employee.departmentId}</TableCell>
              <TableCell>
                <Badge variant={statusVariant[employee.status] ?? 'outline'}>
                  {employee.status.replace('_', ' ')}
                </Badge>
              </TableCell>
              <TableCell>{employee.phone ?? '—'}</TableCell>
              <TableCell className="max-w-[180px] truncate">{employee.email}</TableCell>
              <TableCell>{new Date(employee.hireDate).toLocaleDateString('en-LK')}</TableCell>
              <TableCell>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/employees/${employee.id}`);
                      }}
                    >
                      <Eye className="mr-2 h-4 w-4" />
                      View Profile
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/employees/${employee.id}?edit=true`);
                      }}
                    >
                      <Pencil className="mr-2 h-4 w-4" />
                      Edit
                    </DropdownMenuItem>
                    {onDelete && (
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(employee.id);
                        }}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
