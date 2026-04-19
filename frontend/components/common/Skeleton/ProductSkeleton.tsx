import { BaseSkeleton } from './BaseSkeleton';

interface ProductSkeletonProps {
  className?: string;
}

export function ProductSkeleton({ className = '' }: ProductSkeletonProps) {
  return (
    <div className={`space-y-3 ${className}`}>
      {/* Image placeholder */}
      <BaseSkeleton className="aspect-square w-full rounded-lg" />
      {/* Title */}
      <BaseSkeleton variant="text" className="h-4 w-3/4" />
      {/* Price */}
      <BaseSkeleton variant="text" className="h-4 w-1/3" />
      {/* Rating */}
      <BaseSkeleton variant="text" className="h-3 w-1/2" />
    </div>
  );
}
