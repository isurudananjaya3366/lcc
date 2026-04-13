import { cn } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';

export interface TableSkeletonProps {
  columns?: number;
  rows?: number;
  className?: string;
}

function TableSkeleton({
  columns = 5,
  rows = 5,
  className,
}: TableSkeletonProps) {
  return (
    <div className={cn('rounded-md border', className)}>
      <div className="border-b">
        <div className="flex items-center gap-4 px-4 py-3">
          {Array.from({ length: columns }).map((_, i) => (
            <Skeleton key={`h-${i}`} className="h-4 flex-1" />
          ))}
        </div>
      </div>
      {Array.from({ length: rows }).map((_, ri) => (
        <div key={`r-${ri}`} className="flex items-center gap-4 border-b px-4 py-4 last:border-b-0">
          {Array.from({ length: columns }).map((_, ci) => (
            <Skeleton
              key={`c-${ri}-${ci}`}
              className={cn('h-4 flex-1', ci === 0 && 'max-w-[120px]')}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export { TableSkeleton };
