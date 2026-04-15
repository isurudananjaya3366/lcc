'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowLeft, UserCheck, UserX, Clock, CalendarOff } from 'lucide-react';
import { useAttendance } from '@/hooks/hr/useAttendance';
import { DateRangeSelector } from './DateRangeSelector';
import { AttendanceReportTable } from './AttendanceReportTable';
import { ExportAttendance } from './ExportAttendance';

export function AttendanceReport() {
  const router = useRouter();
  const now = new Date();
  const firstOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().slice(0, 10);
  const today = now.toISOString().slice(0, 10);

  const [startDate, setStartDate] = useState(firstOfMonth);
  const [endDate, setEndDate] = useState(today);

  const { data, isLoading } = useAttendance({ startDate, endDate });
  const records = data?.data ?? [];

  const stats = useMemo(() => {
    const total = records.length;
    const present = records.filter((r) => r.status === 'PRESENT').length;
    const absent = records.filter((r) => r.status === 'ABSENT').length;
    const late = records.filter((r) => r.status === 'LATE').length;
    const onLeave = records.filter((r) => r.status === 'ON_LEAVE').length;
    const totalHours = records.reduce((s, r) => s + (r.workHours ?? 0), 0);
    const avgHours = total > 0 ? totalHours / total : 0;
    const attendanceRate = total > 0 ? ((present + late) / total) * 100 : 0;
    const onTimeRate = total > 0 ? (present / total) * 100 : 0;
    return {
      total,
      present,
      absent,
      late,
      onLeave,
      totalHours,
      avgHours,
      attendanceRate,
      onTimeRate,
    };
  }, [records]);

  const summaryCards = [
    {
      label: 'Present',
      value: stats.present,
      rate: stats.total ? `${((stats.present / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: UserCheck,
      color: 'text-green-600',
    },
    {
      label: 'Absent',
      value: stats.absent,
      rate: stats.total ? `${((stats.absent / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: UserX,
      color: 'text-red-600',
    },
    {
      label: 'Late',
      value: stats.late,
      rate: stats.total ? `${((stats.late / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: Clock,
      color: 'text-yellow-600',
    },
    {
      label: 'On Leave',
      value: stats.onLeave,
      rate: stats.total ? `${((stats.onLeave / stats.total) * 100).toFixed(1)}%` : '0%',
      icon: CalendarOff,
      color: 'text-purple-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push('/attendance')}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Attendance Report</h1>
            <p className="text-muted-foreground">View attendance summary for the selected period</p>
          </div>
        </div>
        <ExportAttendance
          records={records}
          startDate={startDate}
          endDate={endDate}
          disabled={records.length === 0}
        />
      </div>

      <DateRangeSelector
        startDate={startDate}
        endDate={endDate}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {summaryCards.map((c) => (
          <Card key={c.label}>
            <CardContent className="flex items-center gap-4 pt-6">
              <div className={`rounded-lg bg-muted p-3 ${c.color}`}>
                <c.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{c.label}</p>
                <p className="text-2xl font-bold">{c.value}</p>
                <p className="text-xs text-muted-foreground">{c.rate}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-sm text-muted-foreground">Attendance Rate</p>
            <p className="text-3xl font-bold text-green-600">{stats.attendanceRate.toFixed(1)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-sm text-muted-foreground">On-Time %</p>
            <p className="text-3xl font-bold">{stats.onTimeRate.toFixed(1)}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-sm text-muted-foreground">Avg Hours/Day</p>
            <p className="text-3xl font-bold">{stats.avgHours.toFixed(1)}</p>
          </CardContent>
        </Card>
      </div>

      {isLoading ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : (
        <AttendanceReportTable records={records} />
      )}
    </div>
  );
}
