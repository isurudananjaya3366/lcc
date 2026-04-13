import { type LucideIcon, type LucideProps } from 'lucide-react';
import { cn } from '@/lib/utils';

/** Available icon size variants */
export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

const sizeMap: Record<IconSize, number> = {
  xs: 12,
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
};

export interface IconProps extends Omit<LucideProps, 'size'> {
  /** The Lucide icon component to render */
  icon: LucideIcon;
  /** Icon size variant */
  size?: IconSize;
}

/**
 * Reusable Icon wrapper component for consistent icon sizing and styling.
 * Wraps Lucide React icons with standardized size variants.
 */
export function Icon({ icon: LucideIcon, size = 'md', className, ...props }: IconProps) {
  const dimension = sizeMap[size];

  return (
    <LucideIcon
      width={dimension}
      height={dimension}
      className={cn('shrink-0', className)}
      {...props}
    />
  );
}

export default Icon;
