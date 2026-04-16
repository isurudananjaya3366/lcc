import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface HamburgerIconProps {
  isOpen: boolean;
  className?: string;
}

const HamburgerIcon: FC<HamburgerIconProps> = ({ isOpen, className }) => {
  return (
    <div className={cn('relative w-5 h-4 flex flex-col justify-between', className)}>
      <span
        className={cn(
          'block w-full h-0.5 bg-current rounded-full transition-all duration-300 ease-in-out origin-center',
          isOpen && 'translate-y-[7px] rotate-45'
        )}
      />
      <span
        className={cn(
          'block w-full h-0.5 bg-current rounded-full transition-opacity duration-300 ease-in-out',
          isOpen && 'opacity-0'
        )}
      />
      <span
        className={cn(
          'block w-full h-0.5 bg-current rounded-full transition-all duration-300 ease-in-out origin-center',
          isOpen && '-translate-y-[7px] -rotate-45'
        )}
      />
    </div>
  );
};

export default HamburgerIcon;
