'use client';

import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { CalendarDayCell } from './CalendarDayCell';
import { AttendanceLegend } from './AttendanceLegend';
import type { Attendance } from '@/types/hr';

interface AttendanceCalendarProps {
  month: number;
  year: number;
  records: Attendance[];
  onMonthChange: (month: number, year: number) => void;
  onDayClick?: (date: Date) => void;
}

const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function getCalendarDays(month: number, year: number): Date[] {
  const firstDay = new Date(year, month, 1);
  const startDate = new Date(firstDay);
  startDate.setDate(startDate.getDate() - startDate.getDay());

  const days: Date[] = [];
  const current = new Date(startDate);
  for (let i = 0; i < 42; i++) {
    days.push(new Date(current));
    current.setDate(current.getDate() + 1);
  }
  return days;
}

export function AttendanceCalendar({
  month,
  year,
  records,
  onMonthChange,
  onDayClick,
}: AttendanceCalendarProps) {
  const days = useMemo(() => getCalendarDays(month, year), [month, year]);

  const recordsByDate = useMemo(() => {
    const map = new Map<string, Attendance[]>();
    for (const r of records) {
      const key = r.date.slice(0, 10);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(r);
    }
    return map;
  }, [records]);

  const today = new Date();
  const todayStr = today.toISOString().slice(0, 10);

  const prevMonth = () => {
    if (month === 0) onMonthChange(11, year - 1);
    else onMonthChange(month - 1, year);
  };

  const nextMonth = () => {
    if (month === 11) onMonthChange(0, year + 1);
    else onMonthChange(month + 1, year);
  };

  const monthLabel = new Date(year, month).toLocaleDateString('en-LK', {
    month: 'long',
    year: 'numeric',
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base">Attendance Calendar</CardTitle>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={prevMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="w-36 text-center text-sm font-medium">{monthLabel}</span>
          <Button variant="outline" size="icon" onClick={nextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-1">
          {DAY_NAMES.map((d) => (
            <div key={d} className="py-1 text-center text-xs font-medium text-muted-foreground">
              {d}
            </div>
          ))}
          {days.map((date) => {
            const key = date.toISOString().slice(0, 10);
            const dayRecords = recordsByDate.get(key);
            const primaryStatus = dayRecords?.[0]?.status;
            return (
              <CalendarDayCell
                key={key}
                date={date}
                isCurrentMonth={date.getMonth() === month}
                isToday={key === todayStr}
                status={primaryStatus}
                count={dayRecords?.length}
                onClick={onDayClick}
              />
            );
          })}
        </div>
        <div className="mt-4">
          <AttendanceLegend />
        </div>
      </CardContent>
    </Card>
  );
}
