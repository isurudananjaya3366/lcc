'use client';

import { cn } from '@/lib/cn';

interface TrackingStepProps {
  label: string;
  isCompleted: boolean;
  isCurrent: boolean;
  isFirst: boolean;
  isLast: boolean;
}

export function TrackingStep({
  label,
  isCompleted,
  isCurrent,
  isFirst,
  isLast,
}: TrackingStepProps) {
  return (
    <div className="flex flex-1 flex-col items-center">
      <div className="flex w-full items-center">
        {/* Left line */}
        {!isFirst && (
          <div
            className={cn(
              'h-0.5 flex-1',
              isCompleted || isCurrent ? 'bg-green-500' : 'bg-gray-300'
            )}
          />
        )}
        {isFirst && <div className="flex-1" />}

        {/* Circle */}
        <div
          className={cn(
            'flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 transition-colors',
            isCompleted && 'border-green-500 bg-green-500 text-white',
            isCurrent && 'border-blue-500 bg-white text-blue-500',
            !isCompleted && !isCurrent && 'border-gray-300 bg-white text-gray-300'
          )}
        >
          {isCompleted ? (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <div
              className={cn(
                'h-2.5 w-2.5 rounded-full',
                isCurrent ? 'bg-blue-500' : 'bg-gray-300'
              )}
            />
          )}
        </div>

        {/* Right line */}
        {!isLast && (
          <div
            className={cn(
              'h-0.5 flex-1',
              isCompleted ? 'bg-green-500' : 'bg-gray-300'
            )}
          />
        )}
        {isLast && <div className="flex-1" />}
      </div>

      <span
        className={cn(
          'mt-2 text-xs font-medium',
          isCompleted && 'text-green-700',
          isCurrent && 'text-blue-600',
          !isCompleted && !isCurrent && 'text-gray-400'
        )}
      >
        {label}
      </span>
    </div>
  );
}
