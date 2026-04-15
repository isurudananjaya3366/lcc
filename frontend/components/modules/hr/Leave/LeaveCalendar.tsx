'use client';

import { useMemo, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { LeaveRequest } from '@/types/hr';

type CalendarView = 'month' | 'week';

interface LeaveCalendarProps {
  month: number;
  year: number;
  requests: LeaveRequest[];
  onDayClick?: (date: Date) => void;
  onMonthChange?: (month: number) => void;
  onYearChange?: (year: number) => void;
}

const typeColors: Record<string, string> = {
  ANNUAL: 'bg-blue-200 dark:bg-blue-800',
  SICK: 'bg-red-200 dark:bg-red-800',
  UNPAID: 'bg-gray-200 dark:bg-gray-800',
  MATERNITY: 'bg-pink-200 dark:bg-pink-800',
  PATERNITY: 'bg-purple-200 dark:bg-purple-800',
  BEREAVEMENT: 'bg-stone-200 dark:bg-stone-800',
  STUDY: 'bg-indigo-200 dark:bg-indigo-800',
};

const typeLabels: Record<string, string> = {
  ANNUAL: 'Annual',
  SICK: 'Sick',
  UNPAID: 'Unpaid',
  MATERNITY: 'Maternity',
  PATERNITY: 'Paternity',
  BEREAVEMENT: 'Bereavement',
  STUDY: 'Study',
};

const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTH_NAMES = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

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

function getWeekDays(baseDate: Date): Date[] {
  const d = new Date(baseDate);
  d.setDate(d.getDate() - d.getDay());
  const days: Date[] = [];
  for (let i = 0; i < 7; i++) {
    days.push(new Date(d));
    d.setDate(d.getDate() + 1);
  }
  return days;
}

function isDateInRange(date: Date, start: string, end: string): boolean {
  const d = date.toISOString().slice(0, 10);
  return d >= start && d <= end;
}

export function LeaveCalendar({
  month,
  year,
  requests,
  onDayClick,
  onMonthChange,
  onYearChange,
}: LeaveCalendarProps) {
  const [view, setView] = useState<CalendarView>('month');
  const days = useMemo(
    () => (view === 'month' ? getCalendarDays(month, year) : getWeekDays(new Date())),
    [month, year, view]
  );
  const todayStr = new Date().toISOString().slice(0, 10);

  const navigatePrev = () => {
    if (!onMonthChange || !onYearChange) return;
    if (month === 0) {
      onMonthChange(11);
      onYearChange(year - 1);
    } else {
      onMonthChange(month - 1);
    }
  };

  const navigateNext = () => {
    if (!onMonthChange || !onYearChange) return;
    if (month === 11) {
      onMonthChange(0);
      onYearChange(year + 1);
    } else {
      onMonthChange(month + 1);
    }
  };

  const navigateToday = () => {
    const now = new Date();
    onMonthChange?.(now.getMonth());
    onYearChange?.(now.getFullYear());
  };

  return (
    <Card>
      <CardHeader className="space-y-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">Leave Calendar</CardTitle>
          <Select value={view} onValueChange={(v) => setView(v as CalendarView)}>
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="month">Month</SelectItem>
              <SelectItem value="week">Week</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={navigatePrev}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium min-w-[140px] text-center">
              {MONTH_NAMES[month]} {year}
            </span>
            <Button variant="outline" size="icon" className="h-8 w-8" onClick={navigateNext}>
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" className="text-xs" onClick={navigateToday}>
              Today
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-7 gap-1">
          {DAY_NAMES.map((d) => (
            <div key={d} className="py-1 text-center text-xs font-medium text-muted-foreground">
              {d}
            </div>
          ))}
          {days.map((date) => {
            const key = date.toISOString().slice(0, 10);
            const isCurrentMonth = date.getMonth() === month;
            const isToday = key === todayStr;
            const dayRequests = requests.filter((r) => isDateInRange(date, r.startDate, r.endDate));

            return (
              <button
                key={key}
                type="button"
                className={cn(
                  'flex flex-col items-start gap-0.5 rounded-md border p-1 text-left transition-colors hover:bg-muted/50',
                  view === 'month' ? 'h-16' : 'h-24',
                  !isCurrentMonth && view === 'month' && 'opacity-40',
                  isToday && 'border-primary ring-1 ring-primary'
                )}
                onClick={() => onDayClick?.(date)}
              >
                <span className={cn('text-xs', isToday && 'font-bold text-primary')}>
                  {date.getDate()}
                </span>
                {dayRequests.slice(0, view === 'month' ? 2 : 4).map((r) => (
                  <div
                    key={r.id}
                    className={cn(
                      'w-full truncate rounded px-0.5 text-[9px]',
                      typeColors[r.leaveType] ?? 'bg-gray-200'
                    )}
                    title={`${r.employeeId} - ${typeLabels[r.leaveType] ?? r.leaveType}`}
                  >
                    {r.employeeId}
                  </div>
                ))}
                {dayRequests.length > (view === 'month' ? 2 : 4) && (
                  <span className="text-[9px] text-muted-foreground">
                    +{dayRequests.length - (view === 'month' ? 2 : 4)} more
                  </span>
                )}
              </button>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-3 border-t pt-3">
          {Object.entries(typeColors).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1.5">
              <div className={cn('h-3 w-3 rounded-sm', color)} />
              <span className="text-xs text-muted-foreground">{typeLabels[type] ?? type}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
