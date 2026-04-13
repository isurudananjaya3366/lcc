'use client';

import * as React from 'react';
import { CheckCircle2, Clock, XCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

// ================================================================
// Timeline — Vertical chronological event display
// ================================================================

export type TimelineStatus = 'success' | 'pending' | 'error' | 'info';

export interface TimelineItem {
  date: Date | string;
  title: string;
  description?: string;
  icon?: React.ReactNode;
  status?: TimelineStatus;
}

export interface TimelineProps {
  items: TimelineItem[];
  className?: string;
}

const statusConfig: Record<TimelineStatus, { icon: React.ElementType; color: string; dotColor: string }> = {
  success: { icon: CheckCircle2, color: 'text-green-600 dark:text-green-500', dotColor: 'bg-green-600 dark:bg-green-500' },
  pending: { icon: Clock, color: 'text-yellow-600 dark:text-yellow-500', dotColor: 'bg-yellow-600 dark:bg-yellow-500' },
  error: { icon: XCircle, color: 'text-red-600 dark:text-red-500', dotColor: 'bg-red-600 dark:bg-red-500' },
  info: { icon: Info, color: 'text-blue-600 dark:text-blue-500', dotColor: 'bg-blue-600 dark:bg-blue-500' },
};

function formatRelativeDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMs / 3600000);
  const diffDay = Math.floor(diffMs / 86400000);

  if (diffMin < 1) return 'Just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffDay < 7) return `${diffDay}d ago`;

  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    ...(diffDay > 365 ? { year: 'numeric' } : {}),
  });
}

export function Timeline({ items, className }: TimelineProps) {
  return (
    <div className={cn('relative space-y-0', className)}>
      {items.map((item, index) => {
        const status = item.status ?? 'info';
        const config = statusConfig[status];
        const StatusIcon = config.icon;
        const isLast = index === items.length - 1;

        return (
          <div key={index} className="relative flex gap-4 pb-8 last:pb-0">
            {/* Connecting line */}
            {!isLast && (
              <div
                className="absolute left-[15px] top-8 h-[calc(100%-16px)] w-px bg-border"
                aria-hidden="true"
              />
            )}

            {/* Icon / Dot */}
            <div className="relative z-10 flex size-8 shrink-0 items-center justify-center rounded-full border bg-background">
              {item.icon ?? <StatusIcon className={cn('size-4', config.color)} />}
            </div>

            {/* Content */}
            <div className="flex-1 pt-0.5">
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium leading-none">{item.title}</p>
                <time
                  className="text-xs text-muted-foreground shrink-0"
                  dateTime={
                    typeof item.date === 'string'
                      ? item.date
                      : item.date.toISOString()
                  }
                >
                  {formatRelativeDate(item.date)}
                </time>
              </div>
              {item.description && (
                <p className="mt-1 text-sm text-muted-foreground">
                  {item.description}
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
