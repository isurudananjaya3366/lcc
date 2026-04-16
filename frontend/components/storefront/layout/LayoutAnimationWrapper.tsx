'use client';

import React, { type FC, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface LayoutAnimationWrapperProps {
  children: ReactNode;
  className?: string;
  enabled?: boolean;
  animationKey?: string;
}

const LayoutAnimationWrapper: FC<LayoutAnimationWrapperProps> = ({
  children,
  className,
  enabled = true,
  animationKey,
}) => {
  if (!enabled) {
    return <>{children}</>;
  }

  return (
    <div
      key={animationKey}
      className={cn(
        'animate-in fade-in duration-300 ease-out',
        'motion-reduce:animate-none motion-reduce:transition-none',
        className,
      )}
    >
      {children}
    </div>
  );
};

export default LayoutAnimationWrapper;
