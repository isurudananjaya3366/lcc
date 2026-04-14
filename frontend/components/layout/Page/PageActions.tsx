import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

interface PageActionsProps {
  children: ReactNode;
  align?: 'left' | 'center' | 'right';
  className?: string;
}

export function PageActions({ children, align = 'right', className }: PageActionsProps) {
  return (
    <div
      className={cn(
        'flex flex-wrap items-center gap-2',
        align === 'right' && 'justify-end',
        align === 'center' && 'justify-center',
        align === 'left' && 'justify-start',
        className
      )}
    >
      {children}
    </div>
  );
}
