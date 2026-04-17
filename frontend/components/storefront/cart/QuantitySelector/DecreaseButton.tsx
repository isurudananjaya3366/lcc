'use client';

import { cn } from '@/lib/utils';

interface DecreaseButtonProps {
  onClick: () => void;
  disabled?: boolean;
}

export function DecreaseButton({ onClick, disabled = false }: DecreaseButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label="Decrease quantity"
      className={cn(
        'flex h-8 w-8 items-center justify-center rounded-l-md border border-gray-300',
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
        <path
          fillRule="evenodd"
          d="M4 10a.75.75 0 0 1 .75-.75h10.5a.75.75 0 0 1 0 1.5H4.75A.75.75 0 0 1 4 10Z"
          clipRule="evenodd"
        />
      </svg>
    </button>
  );
}
