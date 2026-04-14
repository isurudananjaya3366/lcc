'use client';

import { cn } from '@/lib/cn';

export interface StepIndicatorProps {
  currentStep: number;
  totalSteps: number;
  labels?: string[];
  className?: string;
}

export function StepIndicator({
  currentStep,
  totalSteps,
  labels = ['Business', 'Account', 'Contact', 'Plan'],
  className,
}: StepIndicatorProps) {
  return (
    <nav className={cn('mb-8', className)} aria-label="Registration progress" role="navigation">
      <div className="flex items-center justify-between">
        {Array.from({ length: totalSteps }, (_, i) => {
          const step = i + 1;
          const isCompleted = step < currentStep;
          const isCurrent = step === currentStep;

          return (
            <div key={step} className="flex flex-1 items-center">
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors',
                    isCompleted && 'border-blue-600 bg-blue-600 text-white',
                    isCurrent && 'border-blue-600 bg-white text-blue-600 dark:bg-gray-950',
                    !isCompleted &&
                      !isCurrent &&
                      'border-gray-300 bg-white text-gray-400 dark:border-gray-700 dark:bg-gray-950'
                  )}
                  aria-current={isCurrent ? 'step' : undefined}
                >
                  {isCompleted ? (
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={3}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    step
                  )}
                </div>
                {labels[i] && (
                  <span
                    className={cn(
                      'mt-1 text-xs',
                      isCurrent ? 'font-medium text-blue-600' : 'text-gray-500 dark:text-gray-400'
                    )}
                  >
                    {labels[i]}
                  </span>
                )}
              </div>
              {step < totalSteps && (
                <div
                  className={cn(
                    'mx-2 h-0.5 flex-1',
                    isCompleted ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
    </nav>
  );
}
