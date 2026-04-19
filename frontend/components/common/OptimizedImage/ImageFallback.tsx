import Image from 'next/image';
import { ImageOff } from 'lucide-react';

interface ImageFallbackProps {
  fallbackSrc: string;
  alt: string;
  width?: string | number;
  height?: string | number;
  aspectRatio?: 'square' | 'portrait' | 'landscape' | 'circle';
  onRetry?: () => void;
  className?: string;
}

export function ImageFallback({
  fallbackSrc,
  alt,
  width,
  height,
  aspectRatio = 'square',
  onRetry,
  className = '',
}: ImageFallbackProps) {
  const aspectClass = aspectRatio === 'circle'
    ? 'aspect-square rounded-full'
    : aspectRatio === 'portrait'
      ? 'aspect-[3/4]'
      : aspectRatio === 'landscape'
        ? 'aspect-video'
        : 'aspect-square';

  return (
    <div
      className={`relative flex flex-col items-center justify-center bg-gray-100 dark:bg-gray-800 ${aspectClass} ${className}`}
      role="img"
      aria-label={`Image unavailable: ${alt}`}
    >
      {fallbackSrc ? (
        <Image
          src={fallbackSrc}
          alt={alt}
          width={typeof width === 'number' ? width : 200}
          height={typeof height === 'number' ? height : 200}
          className="object-contain opacity-50"
        />
      ) : (
        <ImageOff className="h-8 w-8 text-gray-400" />
      )}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 text-xs text-blue-600 hover:underline dark:text-blue-400"
        >
          Retry
        </button>
      )}
    </div>
  );
}
