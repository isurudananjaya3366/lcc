'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useDepartments } from '@/hooks/hr/useEmployees';

interface DepartmentFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export function DepartmentFilter({ value, onChange }: DepartmentFilterProps) {
  const { data: departmentsResponse } = useDepartments();
  const departments = departmentsResponse?.data ?? [];

  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[200px]">
        <SelectValue placeholder="All Departments" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">All Departments</SelectItem>
        {departments.map((dept) => (
          <SelectItem key={dept.id} value={dept.id}>
            {dept.name} ({dept.employeeCount})
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
