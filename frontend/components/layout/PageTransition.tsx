'use client';

import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';

/**
 * PageTransition — CSS-based page transition wrapper.
 *
 * Applies a subtle fade-in + slide-up animation on mount.
 * Respects prefers-reduced-motion for accessibility.
 */

interface PageTransitionProps {
  children: ReactNode;
  className?: string;
}

export function PageTransition({ children, className }: PageTransitionProps) {
  return (
    <div
      className={cn(
        'animate-in fade-in slide-in-from-bottom-2 duration-200 ease-out motion-reduce:animate-none',
        className
      )}
    >
      {children}
    </div>
  );
}
