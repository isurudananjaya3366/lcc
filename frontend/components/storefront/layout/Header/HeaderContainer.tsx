'use client';

import React, { type FC, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface HeaderContainerProps {
  children: ReactNode;
  className?: string;
  as?: 'div' | 'nav' | 'section';
}

const HeaderContainer: FC<HeaderContainerProps> = ({ children, className, as: Tag = 'div' }) => {
  return (
    <Tag
      className={cn(
        'mx-auto max-w-7xl flex items-center justify-between px-4 sm:px-6 lg:px-8 xl:px-12',
        className
      )}
    >
      {children}
    </Tag>
  );
};

export default HeaderContainer;
