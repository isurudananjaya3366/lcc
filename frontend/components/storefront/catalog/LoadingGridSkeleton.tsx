import { cn } from '@/lib/utils';
import { ProductCardSkeleton } from './ProductCardSkeleton';

interface LoadingGridSkeletonProps {
  count?: number;
  columns?: 2 | 3 | 4;
  className?: string;
}

export function LoadingGridSkeleton({
  count = 12,
  columns = 4,
  className,
}: LoadingGridSkeletonProps) {
  const gridCols: Record<number, string> = {
    2: 'grid-cols-1 sm:grid-cols-2',
    3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4',
  };

  return (
    <div
      className={cn('grid gap-4', gridCols[columns], className)}
      aria-label="Loading products"
      role="status"
    >
      {Array.from({ length: count }, (_, i) => (
        <ProductCardSkeleton key={i} />
      ))}
      <span className="sr-only">Loading products...</span>
    </div>
  );
}
