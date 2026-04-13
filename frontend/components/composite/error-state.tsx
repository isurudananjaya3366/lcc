'use client';

import * as React from 'react';
import { AlertCircle, RefreshCw, Copy, ChevronDown } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';

export interface ErrorStateProps {
  title?: string;
  message: string;
  error?: Error;
  onRetry?: () => void;
  showDetails?: boolean;
  className?: string;
}

function ErrorState({
  title = 'Something went wrong',
  message,
  error,
  onRetry,
  showDetails = false,
  className,
}: ErrorStateProps) {
  const [detailsOpen, setDetailsOpen] = React.useState(false);
  const isDev = process.env.NODE_ENV === 'development';

  const handleCopy = () => {
    const text = [
      `Error: ${title}`,
      `Message: ${message}`,
      error?.stack ? `Stack: ${error.stack}` : '',
    ]
      .filter(Boolean)
      .join('\n');
    navigator.clipboard.writeText(text);
  };

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 py-12 text-center',
        className
      )}
    >
      <div className="rounded-full bg-destructive/10 p-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
      </div>
      <div className="space-y-1">
        <h3 className="text-lg font-semibold">{title}</h3>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
      <div className="flex items-center gap-2">
        {onRetry && (
          <Button onClick={onRetry} variant="outline" size="sm">
            <RefreshCw className="mr-2 h-4 w-4" />
            Try again
          </Button>
        )}
        {isDev && error && (
          <Button onClick={handleCopy} variant="ghost" size="sm">
            <Copy className="mr-2 h-4 w-4" />
            Copy error
          </Button>
        )}
      </div>
      {(showDetails || isDev) && error?.stack && (
        <div className="mt-2 w-full max-w-lg text-left">
          <button
            type="button"
            onClick={() => setDetailsOpen(!detailsOpen)}
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
          >
            <ChevronDown
              className={cn(
                'h-3 w-3 transition-transform',
                detailsOpen && 'rotate-180'
              )}
            />
            Error details
          </button>
          {detailsOpen && (
            <pre className="mt-1 max-h-48 overflow-auto rounded-md bg-muted p-3 text-xs">
              {error.stack}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export { ErrorState };
