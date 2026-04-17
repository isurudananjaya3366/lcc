'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface CategoryDescriptionProps {
  description: string;
  maxLength?: number;
  className?: string;
}

export function CategoryDescription({
  description,
  maxLength = 250,
  className,
}: CategoryDescriptionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!description) return null;

  const needsTruncation = description.length > maxLength;
  const displayedText =
    needsTruncation && !isExpanded
      ? description.slice(0, description.lastIndexOf(' ', maxLength)) + '...'
      : description;

  return (
    <div className={cn('max-w-4xl', className)}>
      <p className="text-base leading-relaxed text-gray-700 sm:text-lg">{displayedText}</p>

      {needsTruncation && (
        <button
          type="button"
          onClick={() => setIsExpanded((prev) => !prev)}
          className="mt-2 inline-flex items-center gap-1 text-sm font-medium text-blue-600 transition-colors hover:text-blue-800"
        >
          {isExpanded ? (
            <>
              Read less
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 15.75 7.5-7.5 7.5 7.5" />
              </svg>
            </>
          ) : (
            <>
              Read more
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </>
          )}
        </button>
      )}
    </div>
  );
}
