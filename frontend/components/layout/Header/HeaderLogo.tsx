'use client';

import Link from 'next/link';
import { cn } from '@/lib/cn';

/**
 * HeaderLogo — Brand identity in the header bar.
 *
 * Shows the full "LC" mark on mobile (since sidebar logo is hidden),
 * and nothing on desktop (sidebar already has the logo).
 */
export function HeaderLogo() {
  return (
    <Link
      href="/dashboard"
      className={cn(
        'flex items-center gap-2 rounded-lg px-1 transition-opacity lg:hidden',
        'hover:opacity-80',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
      )}
      aria-label="LankaCommerce — Go to Dashboard"
    >
      {/* Logo mark */}
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-sm font-bold text-white">
        LC
      </span>
    </Link>
  );
}
