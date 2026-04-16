'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import type { ScrollPosition, UseScrollPositionOptions } from '@/types/store/layout';

export function useScrollPosition(options?: UseScrollPositionOptions): ScrollPosition {
  const { threshold = 50 } = options ?? {};

  const [position, setPosition] = useState<ScrollPosition>({
    scrollY: 0,
    scrollX: 0,
    scrollDirection: 'none',
    isScrolled: false,
  });

  const prevScrollY = useRef(0);
  const ticking = useRef(false);

  const update = useCallback(() => {
    const currentY = window.scrollY;
    const currentX = window.scrollX;

    let direction: 'up' | 'down' | 'none' = 'none';
    if (currentY > prevScrollY.current) direction = 'down';
    else if (currentY < prevScrollY.current) direction = 'up';

    prevScrollY.current = currentY;

    setPosition({
      scrollY: currentY,
      scrollX: currentX,
      scrollDirection: direction,
      isScrolled: currentY > threshold,
    });

    ticking.current = false;
  }, [threshold]);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleScroll = () => {
      if (!ticking.current) {
        requestAnimationFrame(update);
        ticking.current = true;
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    // Initialize with current scroll position
    update();

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [update]);

  return position;
}
