'use client';

import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/cn';

interface BreadcrumbSeparatorProps {
  className?: string;
}

export function BreadcrumbSeparator({ className }: BreadcrumbSeparatorProps) {
  return (
    <span className={cn('inline-flex mx-2 text-muted-foreground', className)} aria-hidden="true">
      <ChevronRight className="h-4 w-4" />
    </span>
  );
}
