interface ImageSkeletonProps {
  aspectRatio?: 'square' | 'portrait' | 'landscape' | 'circle';
  className?: string;
}

const ASPECT_CLASSES: Record<string, string> = {
  square: 'aspect-square',
  portrait: 'aspect-[3/4]',
  landscape: 'aspect-video',
  circle: 'aspect-square rounded-full',
};

export function ImageSkeleton({ aspectRatio = 'square', className = '' }: ImageSkeletonProps) {
  return (
    <div
      className={`absolute inset-0 animate-pulse bg-gray-200 dark:bg-gray-700 ${ASPECT_CLASSES[aspectRatio] ?? ''} ${className}`}
      role="status"
      aria-label="Loading image"
    >
      <span className="sr-only">Loading image...</span>
    </div>
  );
}
