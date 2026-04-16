import React, { type FC, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface FooterContainerProps {
  children: ReactNode;
  className?: string;
}

const FooterContainer: FC<FooterContainerProps> = ({ children, className }) => {
  return <div className={cn('max-w-7xl mx-auto px-4 md:px-6 lg:px-8', className)}>{children}</div>;
};

export default FooterContainer;
