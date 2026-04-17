'use client';

import React, { type FC } from 'react';
import { Search } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MobileSearchButtonProps {
  onClick: () => void;
  className?: string;
}

const MobileSearchButton: FC<MobileSearchButtonProps> = ({ onClick, className }) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'block p-2 text-gray-600 transition-colors md:hidden',
        'rounded-lg hover:bg-gray-100 hover:text-green-700',
        'dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-green-400',
        className
      )}
      aria-label="Open search"
      title="Search"
    >
      <Search className="h-5 w-5" />
    </button>
  );
};

export default MobileSearchButton;
