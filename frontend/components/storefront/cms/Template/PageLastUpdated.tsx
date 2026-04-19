import { cn } from '@/lib/utils';

interface PageLastUpdatedProps {
  date: string;
  className?: string;
}

export function PageLastUpdated({ date, className }: PageLastUpdatedProps) {
  const formatted = new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <p className={cn('text-sm text-muted-foreground mt-8', className)}>
      Last updated: {formatted}
    </p>
  );
}
