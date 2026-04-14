'use client';

import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';
import { Breadcrumb } from '../Breadcrumb';
import { useBreadcrumbs } from '@/hooks/useBreadcrumbs';

interface PageContainerProps {
  children: ReactNode;
  className?: string;
  showBreadcrumbs?: boolean;
}

export function PageContainer({ children, className, showBreadcrumbs = true }: PageContainerProps) {
  const breadcrumbs = useBreadcrumbs();

  return (
    <div className={cn('space-y-6', className)}>
      {showBreadcrumbs && breadcrumbs.length > 1 && (
        <Breadcrumb items={breadcrumbs} className="px-0" />
      )}
      {children}
    </div>
  );
}
