'use client';

import { cn } from '@/lib/cn';
import { BreadcrumbItem, type BreadcrumbItemData } from './BreadcrumbItem';
import { BreadcrumbSeparator } from './BreadcrumbSeparator';

interface BreadcrumbProps {
  items: BreadcrumbItemData[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  if (items.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className={cn('text-sm', className)}>
      <ol className="flex flex-wrap items-center">
        {items.map((item, i) => (
          <span key={item.href} className="inline-flex items-center">
            {i > 0 && <BreadcrumbSeparator />}
            <BreadcrumbItem item={item} />
          </span>
        ))}
      </ol>
    </nav>
  );
}
