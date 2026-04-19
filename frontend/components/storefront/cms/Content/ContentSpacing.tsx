import { cn } from '@/lib/utils';

interface ContentSpacingProps {
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spacingMap = {
  sm: 'space-y-4',
  md: 'space-y-6',
  lg: 'space-y-8',
} as const;

export function ContentSpacing({ children, size = 'md', className }: ContentSpacingProps) {
  return (
    <div className={cn(spacingMap[size], className)}>
      {children}
    </div>
  );
}
