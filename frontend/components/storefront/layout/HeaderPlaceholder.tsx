'use client';

import { cn } from '@/lib/utils';

export interface HeaderPlaceholderProps {
  className?: string;
}

/**
 * Development-only header placeholder.
 * Replaced by the real Header component in Group B.
 * @see components/storefront/layout/Header/Header.tsx
 */
export default function HeaderPlaceholder({ className }: HeaderPlaceholderProps) {
  const isDev = process.env.NODE_ENV === 'development';

  if (!isDev) {
    return (
      <header className={cn('sticky top-0 z-20 h-16 bg-white shadow-sm', className)}>
        {/* Placeholder for header */}
      </header>
    );
  }

  return (
    <header
      className={cn(
        'sticky top-0 z-20 flex min-h-[64px] items-center justify-center',
        'border-2 border-dashed border-gray-300 bg-white',
        className
      )}
      role="banner"
    >
      <div className="text-center text-sm text-gray-500">
        <p className="font-medium">Header Component (Coming Soon)</p>
        <p className="text-xs text-gray-400">
          See Group B implementation →{' '}
          <code className="rounded bg-gray-100 px-1 py-0.5 text-xs">Header/Header.tsx</code>
        </p>
      </div>
    </header>
  );
}
