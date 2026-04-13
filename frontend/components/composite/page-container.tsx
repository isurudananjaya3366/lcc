import * as React from 'react';
import { cn } from '@/lib/utils';

// ================================================================
// PageContainer — Responsive content wrapper with max-width
// ================================================================

const maxWidthMap = {
  sm: 'max-w-screen-sm',
  md: 'max-w-screen-md',
  lg: 'max-w-screen-lg',
  xl: 'max-w-screen-xl',
  '2xl': 'max-w-screen-2xl',
  full: 'max-w-full',
} as const;

const paddingMap = {
  none: '',
  sm: 'px-4 py-4',
  md: 'px-4 py-6 sm:px-6 lg:px-8',
  lg: 'px-6 py-8 sm:px-8 lg:px-12',
} as const;

export interface PageContainerProps {
  children: React.ReactNode;
  maxWidth?: keyof typeof maxWidthMap;
  padding?: keyof typeof paddingMap;
  className?: string;
}

export function PageContainer({
  children,
  maxWidth = '2xl',
  padding = 'md',
  className,
}: PageContainerProps) {
  return (
    <div
      className={cn(
        'mx-auto w-full',
        maxWidthMap[maxWidth],
        paddingMap[padding],
        className,
      )}
    >
      {children}
    </div>
  );
}
