'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { Employee } from '@/types/hr';

interface EmployeeSelectionStepProps {
  employees: Employee[];
  selectedIds: string[];
  onSelectionChange: (ids: string[]) => void;
}

function formatLKR(amount: number): string {
  return new Intl.NumberFormat('en-LK', {
    style: 'currency',
    currency: 'LKR',
    minimumFractionDigits: 2,
  }).format(amount);
}

export function EmployeeSelectionStep({
  employees,
  selectedIds,
  onSelectionChange,
}: EmployeeSelectionStepProps) {
  const [search, setSearch] = useState('');

  const filtered = employees.filter((e) => {
    const term = search.toLowerCase();
    return (
      e.firstName.toLowerCase().includes(term) ||
      e.lastName.toLowerCase().includes(term) ||
      e.employeeNumber.toLowerCase().includes(term)
    );
  });

  const allSelected = filtered.length > 0 && filtered.every((e) => selectedIds.includes(e.id));

  const toggleAll = () => {
    if (allSelected) {
      const filteredIds = new Set(filtered.map((e) => e.id));
      onSelectionChange(selectedIds.filter((id) => !filteredIds.has(id)));
    } else {
      const merged = new Set([...selectedIds, ...filtered.map((e) => e.id)]);
      onSelectionChange(Array.from(merged));
    }
  };

  const toggleOne = (id: string) => {
    onSelectionChange(
      selectedIds.includes(id) ? selectedIds.filter((sid) => sid !== id) : [...selectedIds, id]
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Select Employees</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <Input
            placeholder="Search employees..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-sm"
          />
          <p className="text-sm text-muted-foreground">
            {selectedIds.length} of {employees.length} selected
          </p>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox checked={allSelected} onCheckedChange={toggleAll} />
                </TableHead>
                <TableHead>Employee</TableHead>
                <TableHead>Department</TableHead>
                <TableHead className="text-right">Salary (LKR)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                    No employees found
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>
                      <Checkbox
                        checked={selectedIds.includes(employee.id)}
                        onCheckedChange={() => toggleOne(employee.id)}
                      />
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">
                          {employee.firstName} {employee.lastName}
                        </p>
                        <p className="text-xs text-muted-foreground">{employee.employeeNumber}</p>
                      </div>
                    </TableCell>
                    <TableCell>{employee.departmentId}</TableCell>
                    <TableCell className="text-right">{formatLKR(employee.salary ?? 0)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
