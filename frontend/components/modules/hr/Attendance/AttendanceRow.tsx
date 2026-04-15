'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Pencil } from 'lucide-react';
import type { Attendance } from '@/types/hr';

interface AttendanceRowProps {
  record: Attendance;
  employeeName?: string;
  onEdit?: (record: Attendance) => void;
}

const statusVariant: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  PRESENT: 'default',
  ABSENT: 'destructive',
  LATE: 'secondary',
  HALF_DAY: 'outline',
  ON_LEAVE: 'secondary',
};

export function AttendanceRow({ record, employeeName, onEdit }: AttendanceRowProps) {
  const formatTime = (time?: string) => {
    if (!time) return '—';
    return new Date(time).toLocaleTimeString('en-LK', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="flex items-center justify-between rounded-lg border p-3">
      <div className="flex items-center gap-4">
        <div>
          <p className="text-sm font-medium">{employeeName ?? record.employeeId}</p>
          <p className="text-xs text-muted-foreground">{record.date}</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right text-sm">
          <p>
            {formatTime(record.checkInTime)} — {formatTime(record.checkOutTime)}
          </p>
          {record.workHours != null && (
            <p className="text-xs text-muted-foreground">{record.workHours.toFixed(1)} hrs</p>
          )}
        </div>
        <Badge variant={statusVariant[record.status] ?? 'outline'}>
          {record.status.replace('_', ' ')}
        </Badge>
        {record.isLate && record.lateMinutes != null && (
          <span className="text-xs text-yellow-600">{record.lateMinutes}m late</span>
        )}
        {onEdit && (
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => onEdit(record)}>
            <Pencil className="h-3.5 w-3.5" />
          </Button>
        )}
      </div>
    </div>
  );
}
