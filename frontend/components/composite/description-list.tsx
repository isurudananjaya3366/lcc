import * as React from 'react';
import { cn } from '@/lib/utils';

// ================================================================
// DescriptionList — Key-value pair display (detail views)
// ================================================================

export interface DescriptionItem {
  label: string;
  value: React.ReactNode;
  className?: string;
}

export interface DescriptionListProps {
  items: DescriptionItem[];
  columns?: 1 | 2 | 3;
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

const columnClasses = {
  1: 'grid-cols-1',
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
} as const;

export function DescriptionList({
  items,
  columns = 1,
  orientation = 'horizontal',
  className,
}: DescriptionListProps) {
  return (
    <dl className={cn('grid gap-4', columnClasses[columns], className)}>
      {items.map((item, index) => (
        <div
          key={index}
          className={cn(
            orientation === 'horizontal'
              ? 'flex items-baseline justify-between gap-4 py-2 border-b border-border last:border-0'
              : 'space-y-1 py-2',
            item.className,
          )}
        >
          <dt className="text-sm font-medium text-muted-foreground shrink-0">
            {item.label}
          </dt>
          <dd
            className={cn(
              'text-sm text-foreground',
              orientation === 'horizontal' && 'text-right',
            )}
          >
            {item.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}
