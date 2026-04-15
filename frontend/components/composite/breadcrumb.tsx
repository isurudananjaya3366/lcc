'use client';

import * as React from 'react';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

// ================================================================
// Breadcrumb — Hierarchical navigation trail
// ================================================================

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  maxVisible?: number;
  className?: string;
}

export function Breadcrumb({ items, separator, maxVisible, className }: BreadcrumbProps) {
  const separatorNode = separator ?? <ChevronRight className="size-3.5 text-muted-foreground/50" />;

  // Responsive collapse: show first, ellipsis, and last items
  const shouldCollapse = maxVisible !== undefined && items.length > maxVisible && maxVisible >= 2;
  const visibleItems = shouldCollapse ? [items[0], ...items.slice(-(maxVisible! - 1))] : items;
  const showEllipsis = shouldCollapse;

  return (
    <nav aria-label="Breadcrumb" className={className}>
      <ol className="flex items-center gap-1.5 text-sm text-muted-foreground flex-wrap">
        {visibleItems.map((item, index) => {
          if (!item) return null;
          const isLast = shouldCollapse
            ? index === visibleItems.length - 1
            : index === items.length - 1;

          return (
            <React.Fragment key={index}>
              {/* Insert ellipsis after first item */}
              {showEllipsis && index === 1 && (
                <>
                  <li aria-hidden="true" className="flex items-center">
                    {separatorNode}
                  </li>
                  <li>
                    <span className="text-muted-foreground/70">…</span>
                  </li>
                </>
              )}

              {index > 0 && (
                <li aria-hidden="true" className="flex items-center">
                  {separatorNode}
                </li>
              )}

              <li className="flex items-center gap-1">
                {item.icon && <span className="size-3.5 shrink-0">{item.icon}</span>}
                {isLast || !item.href ? (
                  <span
                    aria-current={isLast ? 'page' : undefined}
                    className={cn(
                      'truncate',
                      isLast ? 'text-foreground font-medium' : 'text-muted-foreground'
                    )}
                  >
                    {item.label}
                  </span>
                ) : (
                  <Link
                    href={item.href}
                    className="truncate hover:text-foreground transition-colors"
                  >
                    {item.label}
                  </Link>
                )}
              </li>
            </React.Fragment>
          );
        })}
      </ol>
    </nav>
  );
}
