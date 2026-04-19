'use client';

import Image, { type ImageProps } from 'next/image';
import { useState, useCallback } from 'react';
import { ImageSkeleton } from './ImageSkeleton';
import { ImageFallback } from './ImageFallback';

export interface OptimizedImageProps extends Omit<ImageProps, 'onError' | 'onLoad'> {
  fallbackSrc?: string;
  showSkeleton?: boolean;
  aspectRatio?: 'square' | 'portrait' | 'landscape' | 'circle';
  blurDataURL?: string;
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  fallbackSrc = '/images/product-placeholder.svg',
  showSkeleton = true,
  aspectRatio = 'square',
  priority = false,
  blurDataURL,
  className = '',
  ...props
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleLoad = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handleError = useCallback(() => {
    setIsLoading(false);
    setHasError(true);
  }, []);

  const handleRetry = useCallback(() => {
    setHasError(false);
    setIsLoading(true);
  }, []);

  if (hasError) {
    return (
      <ImageFallback
        fallbackSrc={fallbackSrc}
        alt={alt}
        width={width}
        height={height}
        aspectRatio={aspectRatio}
        onRetry={handleRetry}
        className={className}
      />
    );
  }

  return (
    <div className={`relative overflow-hidden ${className}`}>
      {isLoading && showSkeleton && (
        <ImageSkeleton aspectRatio={aspectRatio} />
      )}
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={priority ? 'eager' : 'lazy'}
        priority={priority}
        placeholder={blurDataURL ? 'blur' : 'empty'}
        blurDataURL={blurDataURL}
        onLoad={handleLoad}
        onError={handleError}
        className={`transition-opacity duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        {...props}
      />
    </div>
  );
}
