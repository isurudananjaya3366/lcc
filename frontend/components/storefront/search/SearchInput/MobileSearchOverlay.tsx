'use client';

import React, { useEffect, useRef, type FC } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';
import SearchForm from './SearchForm';

export interface MobileSearchOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

const MobileSearchOverlay: FC<MobileSearchOverlayProps> = ({ isOpen, onClose }) => {
  const overlayRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Body scroll lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Escape to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Focus trap
  useEffect(() => {
    if (!isOpen || !overlayRef.current) return;

    const overlay = overlayRef.current;
    const focusableSelector =
      'a[href], button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      const focusableElements = overlay.querySelectorAll<HTMLElement>(focusableSelector);
      if (focusableElements.length === 0) return;

      const first = focusableElements[0];
      const last = focusableElements[focusableElements.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    };

    document.addEventListener('keydown', handleTab);
    return () => document.removeEventListener('keydown', handleTab);
  }, [isOpen]);

  // Auto-focus the first input on open
  useEffect(() => {
    if (isOpen && overlayRef.current) {
      const input = overlayRef.current.querySelector<HTMLInputElement>('input[type="search"]');
      input?.focus();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      className={cn(
        'fixed inset-0 z-50 flex flex-col bg-white dark:bg-gray-950',
        'animate-in fade-in duration-200'
      )}
      role="dialog"
      aria-modal="true"
      aria-label="Search"
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3 dark:border-gray-800">
        <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">Search</span>
        <button
          ref={closeButtonRef}
          type="button"
          onClick={onClose}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-300"
          aria-label="Close search"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Search form */}
      <div className="px-4 py-4">
        <SearchForm
          onSubmit={() => onClose()}
          size="lg"
          className="max-w-none"
        />
      </div>
    </div>
  );
};

export default MobileSearchOverlay;
