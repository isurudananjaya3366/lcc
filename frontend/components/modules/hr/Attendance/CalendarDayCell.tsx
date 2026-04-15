'use client';

import { cn } from '@/lib/utils';
import type { AttendanceStatus } from '@/types/hr';

interface CalendarDayCellProps {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  status?: AttendanceStatus;
  count?: number;
  onClick?: (date: Date) => void;
}

const statusColors: Record<string, string> = {
  PRESENT: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  ABSENT: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  LATE: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  HALF_DAY: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
  ON_LEAVE: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
};

export function CalendarDayCell({
  date,
  isCurrentMonth,
  isToday,
  status,
  count,
  onClick,
}: CalendarDayCellProps) {
  const day = date.getDate();
  const isWeekend = date.getDay() === 0 || date.getDay() === 6;

  return (
    <button
      type="button"
      className={cn(
        'flex h-20 w-full flex-col items-start gap-1 rounded-md border p-1.5 text-left transition-colors hover:bg-muted/50',
        !isCurrentMonth && 'opacity-40',
        isToday && 'border-primary ring-1 ring-primary',
        isWeekend && !status && 'bg-muted/30'
      )}
      onClick={() => onClick?.(date)}
    >
      <span className={cn('text-xs font-medium', isToday && 'font-bold text-primary')}>{day}</span>
      {status && (
        <span
          className={cn(
            'inline-block rounded px-1 text-[10px] font-medium',
            statusColors[status] ?? 'bg-gray-100 text-gray-800'
          )}
        >
          {status.replace('_', ' ')}
        </span>
      )}
      {count != null && count > 0 && (
        <span className="text-[10px] text-muted-foreground">{count} records</span>
      )}
    </button>
  );
}
