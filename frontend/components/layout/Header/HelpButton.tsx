'use client';

import { HelpCircle } from 'lucide-react';
import { cn } from '@/lib/cn';

export function HelpButton() {
  return (
    <a
      href="/docs"
      className={cn(
        'hidden h-10 w-10 items-center justify-center rounded-lg text-gray-600 transition-colors lg:flex',
        'hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
      )}
      aria-label="Help & Documentation"
    >
      <HelpCircle className="h-5 w-5" />
    </a>
  );
}
