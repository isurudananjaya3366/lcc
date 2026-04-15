'use client';

import { useState, useMemo } from 'react';
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
import { ArrowUpDown, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Attendance } from '@/types/hr';

interface AttendanceReportTableProps {
  records: Attendance[];
}

type SortField = 'date' | 'employeeId' | 'status' | 'workHours';
type SortDir = 'asc' | 'desc';

const PAGE_SIZE = 20;

const statusVariants: Record<string, string> = {
  PRESENT: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  ABSENT: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  LATE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  HALF_DAY: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
  ON_LEAVE: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
};

function formatTime(t?: string): string {
  if (!t) return '—';
  return new Date(t).toLocaleTimeString('en-LK', { hour: '2-digit', minute: '2-digit' });
}

function formatDuration(hours: number | undefined): string {
  if (hours == null) return '—';
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  return `${h}h ${m}m`;
}

export function AttendanceReportTable({ records }: AttendanceReportTableProps) {
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [page, setPage] = useState(1);

  const sorted = useMemo(() => {
    const copy = [...records];
    copy.sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case 'date':
          cmp = (a.date ?? '').localeCompare(b.date ?? '');
          break;
        case 'employeeId':
          cmp = a.employeeId.localeCompare(b.employeeId);
          break;
        case 'status':
          cmp = a.status.localeCompare(b.status);
          break;
        case 'workHours':
          cmp = (a.workHours ?? 0) - (b.workHours ?? 0);
          break;
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return copy;
  }, [records, sortField, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const pageRecords = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir('asc');
    }
    setPage(1);
  };

  if (records.length === 0) {
    return (
      <div className="flex min-h-[200px] items-center justify-center text-muted-foreground">
        No attendance data for the selected period.
      </div>
    );
  }

  const SortHeader = ({ field, label }: { field: SortField; label: string }) => (
    <Button
      variant="ghost"
      size="sm"
      className="-ml-3 h-8 font-medium"
      onClick={() => toggleSort(field)}
    >
      {label}
      <ArrowUpDown className="ml-1 h-3 w-3" />
    </Button>
  );

  return (
    <div className="space-y-3">
      <div className="text-sm text-muted-foreground">
        Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, sorted.length)} of{' '}
        {sorted.length} records
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <SortHeader field="employeeId" label="Employee" />
              </TableHead>
              <TableHead>
                <SortHeader field="date" label="Date" />
              </TableHead>
              <TableHead>Check In</TableHead>
              <TableHead>Check Out</TableHead>
              <TableHead>
                <SortHeader field="workHours" label="Duration" />
              </TableHead>
              <TableHead>
                <SortHeader field="status" label="Status" />
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {pageRecords.map((r, i) => (
              <TableRow key={`${r.employeeId}-${r.date}-${i}`}>
                <TableCell className="font-medium">{r.employeeId}</TableCell>
                <TableCell>
                  {r.date
                    ? new Date(r.date).toLocaleDateString('en-LK', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })
                    : '—'}
                </TableCell>
                <TableCell>{formatTime(r.checkInTime)}</TableCell>
                <TableCell>{formatTime(r.checkOutTime)}</TableCell>
                <TableCell>
                  <span
                    className={cn(
                      'font-mono text-sm',
                      r.workHours && r.workHours > 8
                        ? 'text-amber-600 font-medium'
                        : r.workHours && r.workHours < 4
                          ? 'text-red-600'
                          : ''
                    )}
                  >
                    {formatDuration(r.workHours)}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge className={cn('text-xs', statusVariants[r.status] ?? '')}>
                    {r.status.replace('_', ' ')}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      {totalPages > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
