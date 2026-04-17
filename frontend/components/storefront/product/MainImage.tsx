'use client';

import { useState, useCallback } from 'react';
import Image from 'next/image';
import type { ProductImage } from '@/lib/api/store/modules/products';
import { ImageZoom } from './ImageZoom';
import { ImageLoadingState } from './ImageLoadingState';
import { ImageErrorState } from './ImageErrorState';

interface MainImageProps {
  image: ProductImage;
  productName: string;
  isZoomActive: boolean;
  onZoomToggle: () => void;
  onLightboxOpen: () => void;
}

export function MainImage({
  image,
  productName,
  isZoomActive,
  onZoomToggle,
  onLightboxOpen,
}: MainImageProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleLoad = useCallback(() => {
    setIsLoading(false);
  }, []);

  const handleError = useCallback(() => {
    setIsLoading(false);
    setHasError(true);
  }, []);

  const handleClick = useCallback(() => {
    onLightboxOpen();
  }, [onLightboxOpen]);

  return (
    <div className="relative aspect-square w-full overflow-hidden rounded-lg bg-gray-100 cursor-pointer group">
      {isLoading && <ImageLoadingState className="absolute inset-0 z-10" />}

      {hasError ? (
        <ImageErrorState productName={productName} className="absolute inset-0" />
      ) : (
        <ImageZoom
          image={image}
          productName={productName}
          isActive={isZoomActive}
          onToggle={onZoomToggle}
        >
          <div className="relative w-full h-full" onClick={handleClick}>
            <Image
              src={image.url}
              alt={image.alt_text || productName}
              fill
              sizes="(max-width: 768px) 100vw, 50vw"
              className={`object-cover transition-opacity duration-300 ${
                isLoading ? 'opacity-0' : 'opacity-100'
              }`}
              priority
              onLoad={handleLoad}
              onError={handleError}
            />
          </div>
        </ImageZoom>
      )}

      {/* Expand icon hint */}
      <div className="absolute bottom-3 right-3 z-10 rounded-full bg-black/50 p-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
        </svg>
      </div>
    </div>
  );
}
