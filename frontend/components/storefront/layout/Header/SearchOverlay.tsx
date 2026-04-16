'use client';

import React, { useState, useRef, useEffect, type FC } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import type { SearchOverlayProps } from '@/types/store/header';

const SearchOverlay: FC<SearchOverlayProps> = ({
  isOpen,
  onClose,
  onSearch,
  placeholder = 'Search products...',
}) => {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    onSearch?.(trimmed);
    router.push(`/search?q=${encodeURIComponent(trimmed)}`);
    setQuery('');
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 top-16 bg-black/20 z-40" onClick={onClose} aria-hidden="true" />

      {/* Search panel */}
      <div
        className={cn(
          'fixed left-0 right-0 top-16 z-50 bg-white dark:bg-gray-900 shadow-lg border-b border-gray-200 dark:border-gray-800',
          'animate-in slide-in-from-top duration-200'
        )}
      >
        <div className="container mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="flex items-center gap-3">
            <div className="relative flex-1">
              <input
                ref={inputRef}
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={placeholder}
                className="w-full text-lg py-3 px-4 pl-12 bg-gray-50 dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 dark:text-gray-100"
                aria-label="Search products"
              />
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>

            <button
              type="button"
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              aria-label="Close search"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </>
  );
};

export default SearchOverlay;
