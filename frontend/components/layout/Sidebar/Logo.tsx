'use client';

import Link from 'next/link';
import { cn } from '@/lib/cn';

interface LogoProps {
  isCollapsed: boolean;
}

export function Logo({ isCollapsed }: LogoProps) {
  return (
    <Link
      href="/dashboard"
      className="flex items-center gap-2 rounded-md outline-none focus-visible:ring-2 focus-visible:ring-primary"
      aria-label="LankaCommerce — Go to dashboard"
    >
      {/* Icon mark – always visible */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
        <span className="text-sm font-bold">LC</span>
      </div>

      {/* Full text – hidden when collapsed */}
      <span
        className={cn(
          'whitespace-nowrap font-semibold text-white transition-opacity duration-200',
          isCollapsed ? 'w-0 overflow-hidden opacity-0' : 'opacity-100'
        )}
      >
        LankaCommerce
      </span>
    </Link>
  );
}
