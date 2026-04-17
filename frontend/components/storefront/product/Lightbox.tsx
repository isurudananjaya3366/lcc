'use client';

import { useEffect, useCallback, useRef } from 'react';
import Image from 'next/image';
import type { ProductImage } from '@/lib/api/store/modules/products';
import { LightboxNavigation } from './LightboxNavigation';
import { LightboxControls } from './LightboxControls';

interface LightboxProps {
  images: ProductImage[];
  currentIndex: number;
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (index: number) => void;
}

export function Lightbox({
  images,
  currentIndex,
  isOpen,
  onClose,
  onNavigate,
}: LightboxProps) {
  const overlayRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      document.body.style.overflow = 'hidden';
      overlayRef.current?.focus();
    }
    return () => {
      document.body.style.overflow = '';
      previousActiveElement.current?.focus();
    };
  }, [isOpen]);

  const handlePrev = useCallback(() => {
    onNavigate(currentIndex > 0 ? currentIndex - 1 : images.length - 1);
  }, [currentIndex, images.length, onNavigate]);

  const handleNext = useCallback(() => {
    onNavigate(currentIndex < images.length - 1 ? currentIndex + 1 : 0);
  }, [currentIndex, images.length, onNavigate]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case 'Escape':
          e.preventDefault();
          onClose();
          break;
        case 'ArrowLeft':
          e.preventDefault();
          handlePrev();
          break;
        case 'ArrowRight':
          e.preventDefault();
          handleNext();
          break;
      }
    },
    [onClose, handlePrev, handleNext]
  );

  const handleOverlayClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === overlayRef.current) {
        onClose();
      }
    },
    [onClose]
  );

  if (!isOpen) return null;

  const currentImage = images[currentIndex]!;

  return (
    <div
      ref={overlayRef}
      role="dialog"
      aria-modal="true"
      aria-label="Image lightbox"
      tabIndex={-1}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 animate-fadeIn"
      onClick={handleOverlayClick}
      onKeyDown={handleKeyDown}
      style={{ animationDuration: '200ms' }}
    >
      {/* Controls: counter + close */}
      <LightboxControls
        currentIndex={currentIndex}
        totalImages={images.length}
        onClose={onClose}
      />

      {/* Navigation arrows */}
      {images.length > 1 && (
        <LightboxNavigation
          onPrev={handlePrev}
          onNext={handleNext}
          hasPrev={true}
          hasNext={true}
        />
      )}

      {/* Main image */}
      <div className="relative w-full h-full max-w-[90vw] max-h-[85vh] m-auto flex items-center justify-center p-12">
        <div className="relative w-full h-full">
          <Image
            src={currentImage.url}
            alt={currentImage.alt_text || `Image ${currentIndex + 1}`}
            fill
            sizes="90vw"
            className="object-contain"
            priority
          />
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        .animate-fadeIn {
          animation: fadeIn 200ms ease-out;
        }
      `}</style>
    </div>
  );
}
