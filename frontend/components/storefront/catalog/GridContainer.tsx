import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface GridContainerProps {
  children: ReactNode;
  isEmpty?: boolean;
  emptyMessage?: string;
  className?: string;
}

export function GridContainer({
  children,
  isEmpty,
  emptyMessage = 'No products found.',
  className,
}: GridContainerProps) {
  if (isEmpty) {
    return (
      <div className="flex min-h-[300px] items-center justify-center">
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div
      className={cn(
        'grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-3 xl:grid-cols-4',
        className
      )}
    >
      {children}
    </div>
  );
}
