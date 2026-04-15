'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AttendanceRow } from './AttendanceRow';
import type { Attendance } from '@/types/hr';

interface DailyAttendanceListProps {
  records: Attendance[];
  selectedDate: Date;
  onEditRecord?: (record: Attendance) => void;
}

export function DailyAttendanceList({
  records,
  selectedDate,
  onEditRecord,
}: DailyAttendanceListProps) {
  const dateStr = selectedDate.toLocaleDateString('en-LK', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Daily Attendance — {dateStr}</CardTitle>
      </CardHeader>
      <CardContent>
        {records.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No attendance records for this date.
          </p>
        ) : (
          <div className="space-y-2">
            {records.map((record) => (
              <AttendanceRow key={record.id} record={record} onEdit={onEditRecord} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
