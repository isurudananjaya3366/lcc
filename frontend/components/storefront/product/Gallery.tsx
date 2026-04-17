'use client';

import { useState, useCallback, useEffect, useMemo } from 'react';
import type { ProductImage } from '@/lib/api/store/modules/products';
import { MainImage } from './MainImage';
import { ThumbnailStrip } from './ThumbnailStrip';
import { Lightbox } from './Lightbox';
import { MobileImageSwiper } from './MobileImageSwiper';

interface GalleryProps {
  images: ProductImage[];
  productName: string;
}

export function Gallery({ images, productName }: GalleryProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);
  const [isZoomActive, setIsZoomActive] = useState(false);

  const sortedImages = useMemo(() => {
    if (!images || images.length === 0) return [];
    return [...images].sort((a, b) => {
      if (a.is_primary && !b.is_primary) return -1;
      if (!a.is_primary && b.is_primary) return 1;
      return a.order - b.order;
    });
  }, [images]);

  const handlePrev = useCallback(() => {
    setSelectedIndex((prev) => (prev > 0 ? prev - 1 : sortedImages.length - 1));
  }, [sortedImages.length]);

  const handleNext = useCallback(() => {
    setSelectedIndex((prev) => (prev < sortedImages.length - 1 ? prev + 1 : 0));
  }, [sortedImages.length]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') {
        e.preventDefault();
        handlePrev();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      }
    },
    [handlePrev, handleNext]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  const handleLightboxNavigate = useCallback(
    (index: number) => {
      if (index >= 0 && index < sortedImages.length) {
        setSelectedIndex(index);
      }
    },
    [sortedImages.length]
  );

  if (sortedImages.length === 0) {
    return (
      <div className="aspect-square w-full rounded-lg bg-gray-100 flex items-center justify-center">
        <span className="text-gray-400 text-sm">No images available</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Mobile: swipe gallery with dot indicators */}
      <div className="sm:hidden">
        <MobileImageSwiper
          images={sortedImages}
          productName={productName}
          selectedIndex={selectedIndex}
          onIndexChange={setSelectedIndex}
        />
      </div>

      {/* Desktop: main image + zoom + lightbox */}
      <div className="hidden sm:block">
        <MainImage
          image={sortedImages[selectedIndex]!}
          productName={productName}
          isZoomActive={isZoomActive}
          onZoomToggle={() => setIsZoomActive((prev) => !prev)}
          onLightboxOpen={() => setIsLightboxOpen(true)}
        />
      </div>

      {sortedImages.length > 1 && (
        <ThumbnailStrip
          images={sortedImages}
          selectedIndex={selectedIndex}
          onSelect={setSelectedIndex}
        />
      )}

      {isLightboxOpen && (
        <Lightbox
          images={sortedImages}
          currentIndex={selectedIndex}
          isOpen={isLightboxOpen}
          onClose={() => setIsLightboxOpen(false)}
          onNavigate={handleLightboxNavigate}
        />
      )}
    </div>
  );
}
