import { BaseSkeleton } from './BaseSkeleton';

interface ContentSkeletonProps {
  variant?: 'text' | 'article' | 'media' | 'list';
  lines?: number;
  className?: string;
}

export function ContentSkeleton({
  variant = 'text',
  lines = 4,
  className = '',
}: ContentSkeletonProps) {
  if (variant === 'article') {
    return (
      <div className={`space-y-4 ${className}`}>
        <BaseSkeleton className="h-8 w-2/3" />
        <BaseSkeleton className="h-4 w-1/4" />
        <div className="space-y-2 pt-4">
          {Array.from({ length: lines }).map((_, i) => (
            <BaseSkeleton
              key={i}
              variant="text"
              className={`h-4 ${i === lines - 1 ? 'w-2/3' : 'w-full'}`}
            />
          ))}
        </div>
      </div>
    );
  }

  if (variant === 'media') {
    return (
      <div className={`flex gap-4 ${className}`}>
        <BaseSkeleton className="h-24 w-24 flex-shrink-0 rounded-lg" />
        <div className="flex-1 space-y-2">
          <BaseSkeleton variant="text" className="h-5 w-3/4" />
          <BaseSkeleton variant="text" className="h-4 w-1/2" />
          <BaseSkeleton variant="text" className="h-4 w-full" />
        </div>
      </div>
    );
  }

  if (variant === 'list') {
    return (
      <div className={`space-y-3 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="flex items-center gap-3">
            <BaseSkeleton variant="circular" className="h-10 w-10" />
            <div className="flex-1 space-y-1">
              <BaseSkeleton variant="text" className="h-4 w-2/3" />
              <BaseSkeleton variant="text" className="h-3 w-1/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Default: text variant
  return (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <BaseSkeleton
          key={i}
          variant="text"
          className={`h-4 ${i === lines - 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
}
