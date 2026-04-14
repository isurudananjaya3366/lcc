'use client';

import type { LucideIcon } from 'lucide-react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import Link from 'next/link';
import { cn } from '@/lib/cn';

export interface KPICardProps {
  title: string;
  value: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    label?: string;
  };
  href?: string;
  variant?: 'default' | 'warning' | 'danger' | 'success';
  isLoading?: boolean;
  className?: string;
}

const variantStyles = {
  default: 'border-gray-200 dark:border-gray-700',
  warning: 'border-amber-300 dark:border-amber-700',
  danger: 'border-red-300 dark:border-red-700',
  success: 'border-green-300 dark:border-green-700',
} as const;

const iconBg = {
  default: 'bg-primary/10 text-primary',
  warning: 'bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400',
  danger: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
  success: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
} as const;

const trendColors = {
  up: 'text-green-600 dark:text-green-400',
  down: 'text-red-600 dark:text-red-400',
  neutral: 'text-gray-500 dark:text-gray-400',
} as const;

const TrendIcons = { up: TrendingUp, down: TrendingDown, neutral: Minus } as const;

export function KPICard({
  title,
  value,
  icon: Icon,
  trend,
  href,
  variant = 'default',
  isLoading = false,
  className,
}: KPICardProps) {
  const content = (
    <div
      className={cn(
        'rounded-xl border bg-white p-5 shadow-sm transition-shadow',
        'dark:bg-gray-800',
        variantStyles[variant],
        href && 'cursor-pointer hover:shadow-md',
        className
      )}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</p>
          {isLoading ? (
            <div className="mt-2 h-8 w-24 animate-pulse rounded bg-gray-200 dark:bg-gray-700" />
          ) : (
            <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-gray-100">{value}</p>
          )}
        </div>
        <div
          className={cn(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg',
            iconBg[variant]
          )}
        >
          <Icon className="h-5 w-5" />
        </div>
      </div>

      {trend && !isLoading && (
        <div className="mt-3 flex items-center gap-1 text-xs">
          {(() => {
            const TrendIcon = TrendIcons[trend.direction];
            return (
              <>
                <TrendIcon className={cn('h-3.5 w-3.5', trendColors[trend.direction])} />
                <span className={cn('font-medium', trendColors[trend.direction])}>
                  {Math.abs(trend.value).toFixed(1)}%
                </span>
              </>
            );
          })()}
          {trend.label && <span className="text-gray-500 dark:text-gray-400">{trend.label}</span>}
        </div>
      )}
    </div>
  );

  if (href) {
    return (
      <Link
        href={href}
        className="block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-xl"
      >
        {content}
      </Link>
    );
  }

  return content;
}
