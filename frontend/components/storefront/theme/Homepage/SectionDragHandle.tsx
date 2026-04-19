'use client';

import React from 'react';
import { GripVertical } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SectionDragHandleProps {
  className?: string;
  disabled?: boolean;
}

export function SectionDragHandle({ className, disabled }: SectionDragHandleProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center justify-center h-6 w-6 text-muted-foreground',
        disabled
          ? 'cursor-not-allowed opacity-40'
          : 'cursor-grab active:cursor-grabbing hover:text-foreground',
        className
      )}
      aria-label="Drag to reorder"
      role="button"
      tabIndex={disabled ? -1 : 0}
    >
      <GripVertical className="h-4 w-4" />
    </span>
  );
}
