import { cn } from '@/lib/utils';

interface FilterSkeletonProps {
  sections?: number;
  itemsPerSection?: number;
  showSearch?: boolean;
  className?: string;
}

function SkeletonSection({ items }: { items: number }) {
  return (
    <div className="py-4 border-b border-gray-100 last:border-b-0">
      {/* Section header */}
      <div className="h-4 w-[60%] bg-gray-200 animate-pulse rounded mb-3" />
      {/* Options */}
      <div className="space-y-2.5">
        {Array.from({ length: items }, (_, i) => (
          <div key={i} className="flex items-center gap-2">
            <div className="h-4 w-4 bg-gray-200 animate-pulse rounded" />
            <div
              className="h-3 bg-gray-200 animate-pulse rounded"
              style={{ width: `${40 + Math.random() * 40}%` }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export function FilterSkeleton({
  sections = 4,
  itemsPerSection = 5,
  showSearch = true,
  className,
}: FilterSkeletonProps) {
  return (
    <div className={cn('space-y-1', className)} aria-label="Loading filters" role="status">
      {/* Search box skeleton */}
      {showSearch && (
        <div className="pb-3 border-b border-gray-100">
          <div className="h-9 bg-gray-200 animate-pulse rounded-md" />
        </div>
      )}

      {/* Filter sections */}
      {Array.from({ length: sections }, (_, i) => (
        <SkeletonSection key={i} items={itemsPerSection} />
      ))}

      <span className="sr-only">Loading filters...</span>
    </div>
  );
}
