'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';
import type { MegaMenuProps } from './types/navigation';

const MegaMenu: FC<MegaMenuProps> = ({ isOpen, onClose, children, className }) => {
  if (!isOpen) return null;

  return (
    <div
      className={cn(
        'absolute left-0 right-0 top-full z-50',
        'animate-in fade-in slide-in-from-top-1 duration-200',
        className
      )}
      onMouseLeave={onClose}
    >
      {children}
    </div>
  );
};

export default MegaMenu;
