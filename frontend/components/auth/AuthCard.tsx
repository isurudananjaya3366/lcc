import type { ReactNode } from 'react';

import { cn } from '@/lib/cn';

export interface AuthCardProps {
  children: ReactNode;
  className?: string;
}

export function AuthCard({ children, className }: AuthCardProps) {
  return (
    <div
      className={cn(
        'w-full max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-xl dark:border-gray-800 dark:bg-gray-950 md:p-8',
        className
      )}
    >
      {children}
    </div>
  );
}
