'use client';

import { cn } from '@/lib/utils';

interface DidYouMeanProps {
  suggestion: string | null;
  onSelect: (suggestion: string) => void;
  className?: string;
}

export function DidYouMean({ suggestion, onSelect, className }: DidYouMeanProps) {
  if (!suggestion) return null;

  return (
    <div className={cn('text-sm text-gray-600 dark:text-gray-400', className)}>
      Did you mean:{' '}
      <button
        type="button"
        onClick={() => onSelect(suggestion)}
        className="font-medium text-green-600 underline underline-offset-2 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
      >
        {suggestion}
      </button>
      ?
    </div>
  );
}
