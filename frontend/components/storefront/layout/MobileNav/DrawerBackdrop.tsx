'use client';

import React, { type FC } from 'react';
import { cn } from '@/lib/utils';

interface DrawerBackdropProps {
  onClose: () => void;
  className?: string;
}

const DrawerBackdrop: FC<DrawerBackdropProps> = ({ onClose, className }) => {
  return (
    <div
      className={cn('fixed inset-0 bg-black/50 z-40', 'animate-in fade-in duration-200', className)}
      onClick={onClose}
      aria-hidden="true"
    />
  );
};

export default DrawerBackdrop;
