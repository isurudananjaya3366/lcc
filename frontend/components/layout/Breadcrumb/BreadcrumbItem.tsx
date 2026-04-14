'use client';

import Link from 'next/link';
import { cn } from '@/lib/cn';

export interface BreadcrumbItemData {
  label: string;
  href: string;
  isCurrent: boolean;
}

interface BreadcrumbItemProps {
  item: BreadcrumbItemData;
  className?: string;
}

export function BreadcrumbItem({ item, className }: BreadcrumbItemProps) {
  if (item.isCurrent) {
    return (
      <li className={cn('inline-flex', className)}>
        <span className="truncate text-sm font-medium text-foreground" aria-current="page">
          {item.label}
        </span>
      </li>
    );
  }

  return (
    <li className={cn('inline-flex', className)}>
      <Link
        href={item.href}
        className="truncate text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        {item.label}
      </Link>
    </li>
  );
}
