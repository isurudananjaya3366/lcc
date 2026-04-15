'use client';

import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, X, Users, AlertTriangle } from 'lucide-react';
import { useDepartments } from '@/hooks/hr/useEmployees';

interface AttendanceFilterState {
  search: string;
  status: string;
  department: string;
  dateRange: string;
  attendanceType: string;
}

interface AttendanceFiltersProps {
  filters: AttendanceFilterState;
  onFiltersChange: (filters: AttendanceFilterState) => void;
}

export type { AttendanceFilterState };

const quickFilters = [
  { label: "Today's Absences", icon: Users, filterKey: 'status' as const, value: 'ABSENT' },
  { label: 'Late Today', icon: AlertTriangle, filterKey: 'status' as const, value: 'LATE' },
];

export function AttendanceFilters({ filters, onFiltersChange }: AttendanceFiltersProps) {
  const { data: deptData } = useDepartments();
  const departments = deptData?.data ?? [];

  const hasActive =
    filters.search ||
    filters.status !== 'all' ||
    filters.department !== 'all' ||
    filters.dateRange !== 'all' ||
    filters.attendanceType !== 'all';

  const activeCount = [
    filters.search,
    filters.status !== 'all' && filters.status,
    filters.department !== 'all' && filters.department,
    filters.dateRange !== 'all' && filters.dateRange,
    filters.attendanceType !== 'all' && filters.attendanceType,
  ].filter(Boolean).length;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search employee..."
            value={filters.search}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            className="pl-9"
          />
        </div>

        <Select
          value={filters.status}
          onValueChange={(v) => onFiltersChange({ ...filters, status: v })}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="PRESENT">Present</SelectItem>
            <SelectItem value="ABSENT">Absent</SelectItem>
            <SelectItem value="LATE">Late</SelectItem>
            <SelectItem value="HALF_DAY">Half Day</SelectItem>
            <SelectItem value="ON_LEAVE">On Leave</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={filters.department}
          onValueChange={(v) => onFiltersChange({ ...filters, department: v })}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Departments" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Departments</SelectItem>
            {departments.map((d) => (
              <SelectItem key={d.id} value={d.id}>
                {d.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.dateRange}
          onValueChange={(v) => onFiltersChange({ ...filters, dateRange: v })}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Date Range" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Time</SelectItem>
            <SelectItem value="today">Today</SelectItem>
            <SelectItem value="this_week">This Week</SelectItem>
            <SelectItem value="this_month">This Month</SelectItem>
            <SelectItem value="last_7_days">Last 7 Days</SelectItem>
            <SelectItem value="last_30_days">Last 30 Days</SelectItem>
          </SelectContent>
        </Select>

        <Select
          value={filters.attendanceType}
          onValueChange={(v) => onFiltersChange({ ...filters, attendanceType: v })}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="regular">Regular</SelectItem>
            <SelectItem value="overtime">Overtime</SelectItem>
            <SelectItem value="remote">Remote</SelectItem>
          </SelectContent>
        </Select>

        {hasActive && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() =>
              onFiltersChange({
                search: '',
                status: 'all',
                department: 'all',
                dateRange: 'all',
                attendanceType: 'all',
              })
            }
          >
            <X className="mr-1 h-4 w-4" />
            Clear
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {quickFilters.map((qf) => (
          <Button
            key={qf.label}
            variant="outline"
            size="sm"
            className="text-xs"
            onClick={() => onFiltersChange({ ...filters, [qf.filterKey]: qf.value })}
          >
            <qf.icon className="mr-1 h-3 w-3" />
            {qf.label}
          </Button>
        ))}
        {hasActive && (
          <Badge variant="secondary" className="text-xs">
            {activeCount} filter{activeCount > 1 ? 's' : ''} active
          </Badge>
        )}
      </div>
    </div>
  );
}
