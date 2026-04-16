import React, { type FC, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import LayoutContainer from './LayoutContainer';

export interface MainContentProps {
  children: ReactNode;
  className?: string;
  useContainer?: boolean;
  backgroundColor?: string;
}

const MainContent: FC<MainContentProps> = ({
  children,
  className,
  useContainer = true,
  backgroundColor = 'bg-gray-50',
}) => {
  return (
    <main
      id="main-content"
      role="main"
      tabIndex={-1}
      className={cn(
        'flex-1 pt-6 pb-12 md:pt-8 md:pb-16 focus:outline-none',
        backgroundColor,
        className
      )}
    >
      {useContainer ? <LayoutContainer>{children}</LayoutContainer> : children}
    </main>
  );
};

export default MainContent;
