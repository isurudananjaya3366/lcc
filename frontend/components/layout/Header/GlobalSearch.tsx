'use client';

import { useCallback, useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { cn } from '@/lib/cn';

interface GlobalSearchProps {
  onOpenPalette: () => void;
}

export function GlobalSearch({ onOpenPalette }: GlobalSearchProps) {
  const [isMac, setIsMac] = useState(false);

  useEffect(() => {
    setIsMac(navigator.platform.toUpperCase().includes('MAC'));
  }, []);

  const handleClick = useCallback(() => {
    onOpenPalette();
  }, [onOpenPalette]);

  return (
    <>
      {/* Desktop search bar */}
      <button
        type="button"
        onClick={handleClick}
        className={cn(
          'hidden items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500 transition-colors md:flex',
          'hover:border-gray-300 hover:bg-gray-100',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
          'dark:border-gray-600 dark:bg-gray-700 dark:text-gray-400 dark:hover:border-gray-500 dark:hover:bg-gray-600',
          'w-60 lg:w-72'
        )}
        aria-label="Search — press Ctrl+K"
      >
        <Search className="h-4 w-4 shrink-0" />
        <span className="flex-1 text-left">Search anything...</span>
        <kbd className="pointer-events-none rounded border border-gray-300 bg-gray-200 px-1.5 py-0.5 text-[10px] font-medium text-gray-600 dark:border-gray-500 dark:bg-gray-600 dark:text-gray-300">
          {isMac ? '⌘K' : 'Ctrl+K'}
        </kbd>
      </button>

      {/* Mobile search icon */}
      <button
        type="button"
        onClick={handleClick}
        className={cn(
          'flex h-10 w-10 items-center justify-center rounded-lg text-gray-500 transition-colors md:hidden',
          'hover:bg-gray-100 dark:hover:bg-gray-700',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
        )}
        aria-label="Search"
      >
        <Search className="h-5 w-5" />
      </button>
    </>
  );
}
