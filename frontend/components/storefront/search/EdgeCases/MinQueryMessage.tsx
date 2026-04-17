import { cn } from '@/lib/utils';

interface MinQueryMessageProps {
  minLength?: number;
  className?: string;
}

export function MinQueryMessage({
  minLength = 2,
  className,
}: MinQueryMessageProps) {
  return (
    <p
      className={cn(
        'text-center text-sm text-muted-foreground',
        className,
      )}
      role="status"
      aria-live="polite"
    >
      Please enter at least {minLength} characters to search.
    </p>
  );
}
