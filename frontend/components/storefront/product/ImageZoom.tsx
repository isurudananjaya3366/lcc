'use client';

import { useState, useCallback, useRef, type ReactNode } from 'react';
import Image from 'next/image';
import type { ProductImage } from '@/lib/api/store/modules/products';

interface ImageZoomProps {
  image: ProductImage;
  productName: string;
  isActive: boolean;
  onToggle: () => void;
  children: ReactNode;
}

export function ImageZoom({
  image,
  productName,
  isActive,
  onToggle,
  children,
}: ImageZoomProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoomPosition, setZoomPosition] = useState({ x: 50, y: 50 });
  const [isHovering, setIsHovering] = useState(false);

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!isActive || !containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      setZoomPosition({ x, y });
    },
    [isActive]
  );

  const handleMouseEnter = useCallback(() => {
    setIsHovering(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsHovering(false);
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full hidden md:block"
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onDoubleClick={onToggle}
    >
      {children}

      {/* Zoomed overlay on hover when zoom is active */}
      {isActive && isHovering && (
        <div className="absolute inset-0 z-20 overflow-hidden pointer-events-none">
          <div className="relative w-full h-full">
            <Image
              src={image.url}
              alt={image.alt_text || productName}
              fill
              sizes="100vw"
              className="object-cover"
              style={{
                transformOrigin: `${zoomPosition.x}% ${zoomPosition.y}%`,
                transform: 'scale(2.5)',
              }}
              unoptimized
            />
          </div>
        </div>
      )}

      {/* Zoom toggle hint */}
      {!isActive && (
        <div className="absolute top-3 right-3 z-10 rounded-full bg-black/50 p-1.5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none hidden md:block">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
            <line x1="11" y1="8" x2="11" y2="14" />
            <line x1="8" y1="11" x2="14" y2="11" />
          </svg>
        </div>
      )}

      {/* Mobile: no zoom, just render children */}
      <div className="block md:hidden w-full h-full">{children}</div>
    </div>
  );
}
