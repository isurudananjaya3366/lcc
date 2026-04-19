import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  overlay?: boolean;
  label?: string;
  className?: string;
}

const SIZE_CLASSES = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16',
} as const;

export function LoadingSpinner({
  size = 'md',
  overlay = false,
  label = 'Loading...',
  className,
}: LoadingSpinnerProps) {
  const spinner = (
    <div
      className={cn('flex flex-col items-center justify-center gap-2', className)}
      role="status"
      aria-live="polite"
      aria-label={label}
    >
      <Loader2 className={cn('animate-spin text-primary', SIZE_CLASSES[size])} />
      {size !== 'sm' && (
        <span className="text-sm text-muted-foreground">{label}</span>
      )}
      <span className="sr-only">{label}</span>
    </div>
  );

  if (overlay) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
        {spinner}
      </div>
    );
  }

  return spinner;
}
