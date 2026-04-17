'use client';

import { cn } from '@/lib/utils';
import { useEffect, useCallback, useRef } from 'react';
import { QuickViewContent } from './QuickViewContent';

interface QuickViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  productSlug: string | null;
  className?: string;
}

export function QuickViewModal({ isOpen, onClose, productSlug, className }: QuickViewModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
      contentRef.current?.focus();
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, handleKeyDown]);

  if (!isOpen || !productSlug) return null;

  return (
    <div
      ref={overlayRef}
      className={cn('fixed inset-0 z-50 flex items-center justify-center p-4', className)}
      role="dialog"
      aria-modal="true"
      aria-label="Quick product preview"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 transition-opacity duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal content */}
      <div
        ref={contentRef}
        tabIndex={-1}
        className="relative z-10 w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-lg bg-white shadow-xl transition-all duration-200 scale-100 opacity-100"
      >
        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close quick view"
          className="absolute top-3 right-3 z-20 w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        <QuickViewContent productSlug={productSlug} />
      </div>
    </div>
  );
}
