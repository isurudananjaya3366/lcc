'use client';

import { useState, useId, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface FilterSectionProps {
  title: string;
  badge?: number;
  defaultOpen?: boolean;
  children: ReactNode;
  className?: string;
}

export function FilterSection({
  title,
  badge,
  defaultOpen = true,
  children,
  className,
}: FilterSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const id = useId();
  const headerId = `filter-header-${id}`;
  const contentId = `filter-content-${id}`;

  return (
    <div className={cn('border-b border-gray-200 py-4', className)}>
      <button
        type="button"
        id={headerId}
        aria-expanded={isOpen}
        aria-controls={contentId}
        onClick={() => setIsOpen((v) => !v)}
        className="flex w-full items-center justify-between text-left hover:bg-gray-50 rounded-md px-1 py-1 -mx-1 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1"
      >
        <span className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-900">{title}</span>
          {badge != null && badge > 0 && (
            <span className="inline-flex items-center justify-center rounded-full bg-blue-100 px-2 text-xs font-medium text-blue-700 min-w-[20px] h-5">
              {badge}
            </span>
          )}
        </span>
        {/* Chevron SVG */}
        <svg
          className={cn(
            'h-4 w-4 text-gray-500 transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
          viewBox="0 0 20 20"
          fill="currentColor"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
            clipRule="evenodd"
          />
        </svg>
      </button>
      <div
        id={contentId}
        role="region"
        aria-labelledby={headerId}
        className={cn(
          'overflow-hidden transition-all duration-250 ease-in-out',
          isOpen ? 'max-h-[2000px] opacity-100 mt-3' : 'max-h-0 opacity-0'
        )}
      >
        {children}
      </div>
    </div>
  );
}
