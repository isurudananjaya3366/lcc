'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';

interface CollectionDescriptionProps {
  description?: string;
  story?: string;
  curatorName?: string;
  maxLength?: number;
  className?: string;
}

export function CollectionDescription({
  description,
  story,
  curatorName,
  maxLength = 500,
  className,
}: CollectionDescriptionProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!description && !story) return null;

  const narrativeText = story || '';
  const needsTruncation = narrativeText.length > maxLength;
  const displayedStory =
    needsTruncation && !isExpanded
      ? narrativeText.slice(0, narrativeText.lastIndexOf(' ', maxLength)) + '...'
      : narrativeText;

  return (
    <div className={cn('mx-auto max-w-3xl px-4 py-8 text-center', className)}>
      {/* Short description / summary */}
      {description && (
        <p className="text-lg font-medium leading-relaxed text-gray-800 sm:text-xl">
          {description}
        </p>
      )}

      {/* Full story / narrative */}
      {narrativeText && (
        <div className={cn('mt-4', description && 'mt-6')}>
          <p className="whitespace-pre-line text-base leading-loose text-gray-700 sm:text-lg">
            {displayedStory}
          </p>

          {needsTruncation && (
            <button
              type="button"
              onClick={() => setIsExpanded((prev) => !prev)}
              className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-blue-600 transition-colors hover:text-blue-800"
            >
              {isExpanded ? (
                <>
                  Show less
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m4.5 15.75 7.5-7.5 7.5 7.5"
                    />
                  </svg>
                </>
              ) : (
                <>
                  Read full story
                  <svg
                    className="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="m19.5 8.25-7.5 7.5-7.5-7.5"
                    />
                  </svg>
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Curator attribution */}
      {curatorName && (
        <p className="mt-6 text-base italic text-gray-500">— Curated by {curatorName}</p>
      )}
    </div>
  );
}
