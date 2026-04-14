'use client';

import { useMediaQuery } from './useLayout';

/**
 * Breakpoint presets matching tailwind.config.ts screen values.
 *
 * - xs:  475px
 * - sm:  640px
 * - md:  768px
 * - lg:  1024px  ← primary desktop threshold
 * - xl:  1280px
 * - 2xl: 1536px
 * - 3xl: 1920px
 */

/** True when viewport width < 640px (phone). */
export function useIsMobile(): boolean {
  return useMediaQuery('(max-width: 639px)');
}

/** True when viewport is between 640–1023px (tablet). */
export function useIsTablet(): boolean {
  return useMediaQuery('(min-width: 640px) and (max-width: 1023px)');
}

/** True when viewport >= 1024px (desktop / laptop). */
export function useIsDesktop(): boolean {
  return useMediaQuery('(min-width: 1024px)');
}

/** True when viewport >= 1280px (large desktop). */
export function useIsLargeDesktop(): boolean {
  return useMediaQuery('(min-width: 1280px)');
}

/** True when viewport >= 1920px (ultra-wide). */
export function useIsUltraWide(): boolean {
  return useMediaQuery('(min-width: 1920px)');
}

/** Returns the current Tailwind breakpoint name. */
export type BreakpointName = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl';

export function useCurrentBreakpoint(): BreakpointName {
  const is3xl = useMediaQuery('(min-width: 1920px)');
  const is2xl = useMediaQuery('(min-width: 1536px)');
  const isXl = useMediaQuery('(min-width: 1280px)');
  const isLg = useMediaQuery('(min-width: 1024px)');
  const isMd = useMediaQuery('(min-width: 768px)');
  const isSm = useMediaQuery('(min-width: 640px)');

  if (is3xl) return '3xl';
  if (is2xl) return '2xl';
  if (isXl) return 'xl';
  if (isLg) return 'lg';
  if (isMd) return 'md';
  if (isSm) return 'sm';
  return 'xs';
}
