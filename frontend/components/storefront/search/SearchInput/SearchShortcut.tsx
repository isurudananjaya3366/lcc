'use client';

import { useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';

export interface SearchShortcutProps {
  onOpen: () => void;
  className?: string;
}

const SearchShortcut: FC<SearchShortcutProps> = ({ onOpen, className }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        onOpen();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [onOpen]);

  return (
    <kbd
      className={cn(
        'pointer-events-none hidden select-none items-center gap-0.5 rounded border border-gray-300 bg-gray-100 px-1.5 py-0.5 text-xs font-medium text-gray-500',
        'dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400',
        'sm:inline-flex',
        className
      )}
      aria-hidden="true"
    >
      <span className="text-[10px]">Ctrl</span>
      <span>K</span>
    </kbd>
  );
};

export default SearchShortcut;
