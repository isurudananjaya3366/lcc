'use client';

import { useRef, useCallback, useState } from 'react';
import Image from 'next/image';
import type { ProductImage } from '@/lib/api/store/modules/products';
import { ImageLoadingState } from './ImageLoadingState';
import { ImageErrorState } from './ImageErrorState';

interface MobileImageSwiperProps {
  images: ProductImage[];
  productName: string;
  selectedIndex: number;
  onIndexChange: (index: number) => void;
}

const SWIPE_THRESHOLD = 50;

export function MobileImageSwiper({
  images,
  productName,
  selectedIndex,
  onIndexChange,
}: MobileImageSwiperProps) {
  const touchStartX = useRef(0);
  const touchEndX = useRef(0);
  const isDragging = useRef(false);
  const [translateX, setTranslateX] = useState(0);
  const [isSwiping, setIsSwiping] = useState(false);
  const [loadingStates, setLoadingStates] = useState<Record<number, boolean>>({});
  const [errorStates, setErrorStates] = useState<Record<number, boolean>>({});

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    touchStartX.current = e.touches[0]!.clientX;
    touchEndX.current = e.touches[0]!.clientX;
    isDragging.current = true;
    setIsSwiping(true);
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (!isDragging.current) return;
    touchEndX.current = e.touches[0]!.clientX;
    const diff = touchEndX.current - touchStartX.current;
    setTranslateX(diff);
  }, []);

  const handleTouchEnd = useCallback(() => {
    if (!isDragging.current) return;
    isDragging.current = false;
    setIsSwiping(false);

    const diff = touchEndX.current - touchStartX.current;

    if (Math.abs(diff) > SWIPE_THRESHOLD) {
      if (diff < 0 && selectedIndex < images.length - 1) {
        // Swipe left → next
        onIndexChange(selectedIndex + 1);
      } else if (diff > 0 && selectedIndex > 0) {
        // Swipe right → prev
        onIndexChange(selectedIndex - 1);
      }
    }

    setTranslateX(0);
  }, [selectedIndex, images.length, onIndexChange]);

  const handleImageLoad = useCallback((index: number) => {
    setLoadingStates((prev) => ({ ...prev, [index]: false }));
  }, []);

  const handleImageError = useCallback((index: number) => {
    setLoadingStates((prev) => ({ ...prev, [index]: false }));
    setErrorStates((prev) => ({ ...prev, [index]: true }));
  }, []);

  if (images.length === 0) {
    return (
      <div className="aspect-square w-full rounded-lg bg-gray-100 flex items-center justify-center">
        <span className="text-gray-400 text-sm">No images</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {/* Swipeable image area */}
      <div
        className="relative aspect-square w-full overflow-hidden rounded-lg bg-gray-100"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        <div
          className="flex h-full"
          style={{
            width: `${images.length * 100}%`,
            transform: `translateX(calc(-${selectedIndex * (100 / images.length)}% + ${isSwiping ? translateX : 0}px))`,
            transition: isSwiping ? 'none' : 'transform 300ms ease-out',
          }}
        >
          {images.map((image, index) => (
            <div
              key={image.id}
              className="relative h-full"
              style={{ width: `${100 / images.length}%` }}
            >
              {loadingStates[index] !== false && (
                <ImageLoadingState className="absolute inset-0 z-10" />
              )}
              {errorStates[index] ? (
                <ImageErrorState productName={productName} className="absolute inset-0" />
              ) : (
                <Image
                  src={image.url}
                  alt={image.alt_text || `${productName} - Image ${index + 1}`}
                  fill
                  sizes="100vw"
                  className="object-cover"
                  priority={index === 0}
                  onLoad={() => handleImageLoad(index)}
                  onError={() => handleImageError(index)}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Dot indicators */}
      {images.length > 1 && (
        <div className="flex items-center justify-center gap-1.5 py-1" role="tablist">
          {images.map((_, index) => (
            <button
              key={index}
              role="tab"
              aria-selected={index === selectedIndex}
              aria-label={`Go to image ${index + 1}`}
              onClick={() => onIndexChange(index)}
              className={`rounded-full transition-all duration-200 ${
                index === selectedIndex
                  ? 'w-2.5 h-2.5 bg-gray-900'
                  : 'w-2 h-2 bg-gray-300 hover:bg-gray-400'
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
}
