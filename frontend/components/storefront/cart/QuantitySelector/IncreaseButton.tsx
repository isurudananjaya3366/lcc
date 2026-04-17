'use client';

import { cn } from '@/lib/utils';

interface IncreaseButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function IncreaseButton({ onClick, disabled = false }: IncreaseButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label="Increase quantity"
      className={cn(
        'flex h-8 w-8 items-center justify-center rounded-r-md border border-gray-300',
        'transition-colors duration-150',
        'dark:border-gray-600',
        disabled
          ? 'cursor-not-allowed bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600'
          : 'bg-white text-gray-700 hover:bg-gray-100 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
      )}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        className="h-4 w-4"
        aria-hidden="true"
      >
        <path d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z" />
      </svg>
    </button>
  );
}
