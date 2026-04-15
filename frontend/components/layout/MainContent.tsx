import type { ReactNode } from 'react';
import { cn } from '@/lib/cn';
import { PageTransition } from './PageTransition';

/**
 * MainContent — Scrollable content container for dashboard pages.
 *
 * Wraps page content with consistent padding, scrolling, and
 * background styling. Renders as a semantic <main> element.
 */

export interface MainContentProps {
  children: ReactNode;
  className?: string;
  /** Remove default padding for full-width content. */
  noPadding?: boolean;
}

export function MainContent({ children, className, noPadding }: MainContentProps) {
  return (
    <main
      id="main-content"
      tabIndex={-1}
      className={cn(
        'relative flex-1 overflow-y-auto overflow-x-hidden bg-gray-50 focus:outline-none dark:bg-gray-900',
        !noPadding && 'p-4 md:p-6 lg:p-8 xl:p-10',
        className
      )}
    >
      <div className="mx-auto max-w-screen-2xl">
        <PageTransition>{children}</PageTransition>
      </div>
    </main>
  );
}
