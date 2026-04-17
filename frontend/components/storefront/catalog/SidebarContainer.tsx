import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface SidebarContainerProps {
  children: ReactNode;
  title?: string;
  className?: string;
}

export function SidebarContainer({ children, title, className }: SidebarContainerProps) {
  return (
    <div
      className={cn(
        'rounded-lg border bg-white p-4 lg:sticky lg:top-24 lg:max-h-[calc(100vh-120px)] lg:overflow-y-auto lg:p-6',
        className
      )}
    >
      {title && <h3 className="mb-4 text-lg font-semibold">{title}</h3>}
      <div className="space-y-6">{children}</div>
    </div>
  );
}
