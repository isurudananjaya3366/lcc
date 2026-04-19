'use client';

import { cn } from '@/lib/utils';

interface ColorSwatchPreviewProps {
  color: string;
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

const sizeMap = {
  sm: 'w-6 h-6',
  md: 'w-10 h-10',
  lg: 'w-[60px] h-[60px]',
} as const;

export function ColorSwatchPreview({
  color,
  size = 'md',
  onClick,
  disabled = false,
  className,
}: ColorSwatchPreviewProps) {
  const isInteractive = !!onClick && !disabled;

  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={`Color swatch: ${color}`}
      className={cn(
        'relative rounded-lg border-2 border-gray-300 transition-transform',
        sizeMap[size],
        isInteractive &&
          'cursor-pointer hover:scale-105 active:scale-95 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
        disabled && 'opacity-50 cursor-not-allowed',
        !isInteractive && !disabled && 'cursor-default',
        className
      )}
      style={{ backgroundColor: color }}
    />
  );
}
