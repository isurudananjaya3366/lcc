import { cn } from '@/lib/utils';

interface ProductCountProps {
  count?: number;
  isLoading?: boolean;
  className?: string;
}

export function ProductCount({ count, isLoading, className }: ProductCountProps) {
  if (count === undefined && !isLoading) return null;

  if (isLoading) {
    return (
      <span className={cn('inline-block h-5 w-24 animate-pulse rounded bg-gray-200', className)} />
    );
  }

  const formatted = count!.toLocaleString();
  const label = count === 1 ? 'product' : 'products';

  return (
    <p className={cn('text-sm text-gray-600 md:text-base', className)}>
      {formatted} {label}
    </p>
  );
}
