'use client';

import { toast } from 'sonner';
import { cn } from '@/lib/utils';

interface SaveForLaterProps {
  onClick?: () => void;
}

export function SaveForLater({ onClick }: SaveForLaterProps) {
  const handleClick = () => {
    onClick?.();
    toast('Item saved for later', {
      description: 'You can find it in your wishlist.',
    });
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      aria-label="Save for later"
      className={cn(
        'inline-flex items-center gap-1 text-sm text-gray-600 transition-colors',
        'hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
      )}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 20 20"
        fill="currentColor"
        className="h-4 w-4"
        aria-hidden="true"
      >
        <path d="M9.653 16.915l-.005-.003-.019-.01a20.759 20.759 0 0 1-1.162-.682 22.045 22.045 0 0 1-2.582-1.9C4.045 12.733 2 10.352 2 7.5a4.5 4.5 0 0 1 8-2.828A4.5 4.5 0 0 1 18 7.5c0 2.852-2.044 5.233-3.885 6.82a22.049 22.049 0 0 1-3.744 2.582l-.019.01-.005.003h-.002a.723.723 0 0 1-.69 0h-.002Z" />
      </svg>
      Save for Later
    </button>
  );
}
