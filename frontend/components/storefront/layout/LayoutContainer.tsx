import React, { type FC, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import type { ContainerMaxWidth } from '@/types/store/layout';

export interface LayoutContainerProps {
  children: ReactNode;
  className?: string;
  maxWidth?: ContainerMaxWidth;
  padding?: boolean;
}

const maxWidthClasses: Record<ContainerMaxWidth, string> = {
  sm: 'max-w-screen-sm',
  md: 'max-w-screen-md',
  lg: 'max-w-screen-lg',
  xl: 'max-w-screen-xl',
  '2xl': 'max-w-screen-2xl',
  full: 'w-full',
};

const LayoutContainer: FC<LayoutContainerProps> = ({
  children,
  className,
  maxWidth = '2xl',
  padding = true,
}) => {
  return (
    <div
      className={cn(
        'mx-auto transition-all duration-200',
        maxWidthClasses[maxWidth],
        padding && 'px-4 md:px-6 lg:px-8',
        className
      )}
    >
      {children}
    </div>
  );
};

export default LayoutContainer;
