'use client';

import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface KPISummaryProps {
  children: ReactNode;
  className?: string;
}

/**
 * Responsive grid container for KPI cards.
 * 1 column on mobile, 2 on tablet, 4 on desktop.
 */
export function KPISummary({ children, className }: KPISummaryProps) {
  return (
    <div className={cn('grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4', className)}>
      {children}
    </div>
  );
}
