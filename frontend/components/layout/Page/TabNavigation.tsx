'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

export interface TabItem {
  label: string;
  value: string;
  href: string;
  icon?: ReactNode;
  badge?: number | string;
}

interface TabNavigationProps {
  tabs: TabItem[];
  className?: string;
}

export function TabNavigation({ tabs, className }: TabNavigationProps) {
  const pathname = usePathname();

  return (
    <nav className={cn('border-b', className)} aria-label="Tab navigation">
      <div className="-mb-px flex gap-1 overflow-x-auto">
        {tabs.map((tab) => {
          const isActive = pathname === tab.href || pathname.startsWith(tab.href + '/');
          return (
            <Link
              key={tab.value}
              href={tab.href}
              className={cn(
                'inline-flex shrink-0 items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2'
              )}
              aria-current={isActive ? 'page' : undefined}
            >
              {tab.icon}
              {tab.label}
              {tab.badge != null && (
                <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-semibold tabular-nums">
                  {tab.badge}
                </span>
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
