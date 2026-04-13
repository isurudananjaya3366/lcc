'use client';

import * as React from 'react';
import { type LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

import { cn } from '@/lib/utils';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export interface StatCardProps {
  title: string;
  value: number;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  icon?: LucideIcon;
  description?: string;
  prefix?: string;
  suffix?: string;
  className?: string;
}

function formatValue(value: number, prefix?: string, suffix?: string): string {
  let formatted: string;
  const abs = Math.abs(value);
  if (abs >= 1_000_000) {
    formatted = `${(value / 1_000_000).toFixed(2)}M`;
  } else if (abs >= 1_000) {
    formatted = `${(value / 1_000).toFixed(1)}K`;
  } else {
    formatted = value.toLocaleString();
  }
  return `${prefix ?? ''}${formatted}${suffix ?? ''}`;
}

const trendConfig = {
  up: {
    icon: TrendingUp,
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-50 dark:bg-green-950/30',
  },
  down: {
    icon: TrendingDown,
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-50 dark:bg-red-950/30',
  },
  neutral: {
    icon: Minus,
    color: 'text-muted-foreground',
    bg: 'bg-muted',
  },
} as const;

function StatCard({
  title,
  value,
  change,
  trend = 'neutral',
  icon: Icon,
  description,
  prefix,
  suffix,
  className,
}: StatCardProps) {
  const trendInfo = trendConfig[trend];
  const TrendIcon = trendInfo.icon;

  return (
    <Card className={cn('', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && (
          <Icon className="h-4 w-4 text-muted-foreground" />
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {formatValue(value, prefix, suffix)}
        </div>
        <div className="flex items-center gap-2 pt-1">
          {change !== undefined && (
            <span
              className={cn(
                'inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 text-xs font-medium',
                trendInfo.bg,
                trendInfo.color
              )}
            >
              <TrendIcon className="h-3 w-3" />
              {Math.abs(change).toFixed(1)}%
            </span>
          )}
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export { StatCard };
