'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { cn } from '@/lib/utils';

export interface ScrollToTopProps {
  showAfter?: number;
  className?: string;
}

export function ScrollToTop({ showAfter = 400, className }: ScrollToTopProps) {
  const [isVisible, setIsVisible] = useState(false);
  const ticking = useRef(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleScroll = () => {
      if (!ticking.current) {
        requestAnimationFrame(() => {
          setIsVisible(window.scrollY > showAfter);
          ticking.current = false;
        });
        ticking.current = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    // Check initial position
    handleScroll();

    return () => window.removeEventListener('scroll', handleScroll);
  }, [showAfter]);

  const scrollToTop = useCallback(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  if (!isVisible) return null;

  return (
    <button
      type="button"
      onClick={scrollToTop}
      className={cn(
        'flex items-center justify-center rounded-full shadow-lg',
        'h-10 w-10 md:h-11 md:w-11',
        'bg-blue-600 text-white',
        'transition-all duration-200 hover:scale-105 hover:brightness-110',
        'focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-2',
        'animate-in fade-in slide-in-from-bottom-2 duration-300',
        className
      )}
      aria-label="Scroll to top"
      role="button"
      tabIndex={0}
    >
      {/* Arrow Up Icon */}
      <svg
        className="h-5 w-5 md:h-5 md:w-5"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth={2.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M18 15l-6-6-6 6" />
      </svg>
    </button>
  );
}

export default ScrollToTop;
