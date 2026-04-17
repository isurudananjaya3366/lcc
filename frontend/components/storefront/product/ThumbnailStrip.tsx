'use client';

import { useRef, useState, useCallback, useEffect } from 'react';
import type { ProductImage } from '@/lib/api/store/modules/products';
import { ThumbnailItem } from './ThumbnailItem';

interface ThumbnailStripProps {
  images: ProductImage[];
  selectedIndex: number;
  onSelect: (index: number) => void;
}

export function ThumbnailStrip({ images, selectedIndex, onSelect }: ThumbnailStripProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);

  const checkScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 1);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
  }, []);

  useEffect(() => {
    checkScroll();
    const el = scrollRef.current;
    if (!el) return;
    el.addEventListener('scroll', checkScroll, { passive: true });
    const resizeObserver = new ResizeObserver(checkScroll);
    resizeObserver.observe(el);
    return () => {
      el.removeEventListener('scroll', checkScroll);
      resizeObserver.disconnect();
    };
  }, [checkScroll, images.length]);

  // Scroll selected thumbnail into view
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const thumb = el.children[selectedIndex] as HTMLElement | undefined;
    if (thumb) {
      thumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
    }
  }, [selectedIndex]);

  const scroll = useCallback((direction: 'left' | 'right') => {
    const el = scrollRef.current;
    if (!el) return;
    const scrollAmount = el.clientWidth * 0.6;
    el.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth',
    });
  }, []);

  return (
    <div className="relative group/thumbnails">
      {/* Scroll left button */}
      {canScrollLeft && (
        <button
          onClick={() => scroll('left')}
          aria-label="Scroll thumbnails left"
          className="absolute left-0 top-1/2 -translate-y-1/2 z-10 rounded-full bg-white shadow-md p-1 opacity-0 group-hover/thumbnails:opacity-100 transition-opacity"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      )}

      {/* Thumbnails container */}
      <div
        ref={scrollRef}
        className="flex gap-2 overflow-x-auto scrollbar-hide scroll-smooth"
        style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
      >
        {images.map((image, index) => (
          <ThumbnailItem
            key={image.id}
            image={image}
            isSelected={index === selectedIndex}
            onClick={() => onSelect(index)}
          />
        ))}
      </div>

      {/* Scroll right button */}
      {canScrollRight && (
        <button
          onClick={() => scroll('right')}
          aria-label="Scroll thumbnails right"
          className="absolute right-0 top-1/2 -translate-y-1/2 z-10 rounded-full bg-white shadow-md p-1 opacity-0 group-hover/thumbnails:opacity-100 transition-opacity"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      )}
    </div>
  );
}
