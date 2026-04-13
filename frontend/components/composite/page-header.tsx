'use client';

import * as React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

// ================================================================
// PageHeader — Page title with breadcrumb, description & actions
// ================================================================

export interface BreadcrumbNavItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export interface PageHeaderProps {
  title: string;
  description?: string;
  breadcrumb?: BreadcrumbNavItem[];
  actions?: React.ReactNode;
  backHref?: string;
  className?: string;
}

export function PageHeader({
  title,
  description,
  breadcrumb,
  actions,
  backHref,
  className,
}: PageHeaderProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {/* Breadcrumb */}
      {breadcrumb && breadcrumb.length > 0 && (
        <nav aria-label="Breadcrumb">
          <ol className="flex items-center gap-1.5 text-sm text-muted-foreground">
            {breadcrumb.map((item, index) => {
              const isLast = index === breadcrumb.length - 1;
              return (
                <li key={index} className="flex items-center gap-1.5">
                  {index > 0 && (
                    <span aria-hidden="true" className="text-muted-foreground/50">
                      /
                    </span>
                  )}
                  {item.icon && <span className="size-3.5">{item.icon}</span>}
                  {isLast || !item.href ? (
                    <span aria-current={isLast ? 'page' : undefined} className={cn(isLast && 'text-foreground font-medium')}>
                      {item.label}
                    </span>
                  ) : (
                    <Link href={item.href} className="hover:text-foreground transition-colors">
                      {item.label}
                    </Link>
                  )}
                </li>
              );
            })}
          </ol>
        </nav>
      )}

      {/* Header row */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          {backHref && (
            <Link
              href={backHref}
              className="inline-flex size-8 items-center justify-center rounded-md border border-input bg-background text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft className="size-4" />
            </Link>
          )}
          <div className="space-y-1">
            <h1 className="text-2xl font-bold tracking-tight lg:text-3xl">{title}</h1>
            {description && (
              <p className="text-sm text-muted-foreground lg:text-base">{description}</p>
            )}
          </div>
        </div>

        {actions && (
          <div className="flex items-center gap-2 shrink-0">{actions}</div>
        )}
      </div>
    </div>
  );
}
