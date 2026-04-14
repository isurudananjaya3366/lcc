import { Loader2 } from 'lucide-react';

import { cn } from '@/lib/cn';

export interface AuthLoadingProps {
  message?: string;
  fullscreen?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const spinnerSizeMap = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
} as const;

export function AuthLoading({
  message = 'Loading...',
  fullscreen = false,
  size = 'md',
  className,
}: AuthLoadingProps) {
  const content = (
    <div className={cn('flex flex-col items-center justify-center gap-3', className)}>
      <Loader2 className={cn('animate-spin text-blue-600', spinnerSizeMap[size])} />
      {message && <p className="text-sm text-gray-600 dark:text-gray-400">{message}</p>}
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
        {content}
      </div>
    );
  }

  return content;
}
