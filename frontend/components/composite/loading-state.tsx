import { Loader2 } from 'lucide-react';

import { cn } from '@/lib/utils';

export interface LoadingStateProps {
  message?: string;
  fullPage?: boolean;
  overlay?: boolean;
  size?: 'sm' | 'default' | 'lg';
  className?: string;
}

const sizeMap = {
  sm: 'h-6 w-6',
  default: 'h-10 w-10',
  lg: 'h-16 w-16',
} as const;

function LoadingState({
  message = 'Loading...',
  fullPage = false,
  overlay = false,
  size = 'default',
  className,
}: LoadingStateProps) {
  const content = (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3',
        className
      )}
      role="status"
      aria-live="polite"
    >
      <Loader2
        className={cn('animate-spin text-muted-foreground', sizeMap[size])}
      />
      {message && (
        <p className="text-sm text-muted-foreground">{message}</p>
      )}
      <span className="sr-only">{message}</span>
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background">
        {content}
      </div>
    );
  }

  if (overlay) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
        {content}
      </div>
    );
  }

  return <div className="flex min-h-[200px] items-center justify-center">{content}</div>;
}

export { LoadingState };
