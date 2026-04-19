import { ProductSkeleton } from './ProductSkeleton';

interface GridSkeletonProps {
  count?: number;
  columns?: 2 | 3 | 4;
  className?: string;
  itemComponent?: React.ComponentType<{ className?: string }>;
}

const COLUMN_CLASSES = {
  2: 'grid-cols-1 sm:grid-cols-2',
  3: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
  4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
} as const;

export function GridSkeleton({
  count = 8,
  columns = 4,
  className = '',
  itemComponent: ItemComponent = ProductSkeleton,
}: GridSkeletonProps) {
  return (
    <div className={`grid gap-4 md:gap-6 ${COLUMN_CLASSES[columns]} ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <ItemComponent key={i} />
      ))}
    </div>
  );
}
