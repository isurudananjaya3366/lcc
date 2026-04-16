'use client';

import { useMemo } from 'react';
import { useScrollPosition } from './useScrollPosition';
import type { UseStickyHeaderOptions, StickyHeaderState } from '@/types/store/layout';

export function useStickyHeader(options?: UseStickyHeaderOptions): StickyHeaderState {
  const { behavior = 'always-visible', threshold = 50 } = options ?? {};

  const { scrollY, scrollDirection, isScrolled } = useScrollPosition({ threshold });

  const state = useMemo<StickyHeaderState>(() => {
    const isSticky = isScrolled;
    let isVisible = true;

    switch (behavior) {
      case 'always-visible':
        isVisible = true;
        break;
      case 'hide-on-scroll-down':
        if (scrollY < threshold) {
          isVisible = true;
        } else {
          isVisible = scrollDirection !== 'down';
        }
        break;
      case 'sticky':
        isVisible = true;
        break;
    }

    return {
      isSticky,
      isVisible,
      shouldAnimate: isSticky,
      headerOffset: isVisible ? 0 : -100,
    };
  }, [behavior, scrollY, scrollDirection, isScrolled, threshold]);

  return state;
}
