'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface CloseDrawerButtonProps {
  onClose: () => void;
  className?: string;
}

const CloseDrawerButton: FC<CloseDrawerButtonProps> = ({ onClose, className }) => {
  return (
    <button
      type="button"
      onClick={onClose}
      className={cn(
        'flex items-center justify-center w-11 h-11 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-200 transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-gray-300',
        className
      )}
      aria-label="Close menu"
      aria-controls="mobile-nav-drawer"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-5 w-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M6 18L18 6M6 6l12 12"
        />
      </svg>
    </button>
  );
};

export default CloseDrawerButton;
