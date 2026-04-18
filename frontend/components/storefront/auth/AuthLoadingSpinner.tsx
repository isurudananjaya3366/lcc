'use client';

import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/cn';

export interface AuthLoadingSpinnerProps {
  message?: string;
  className?: string;
}

export function AuthLoadingSpinner({
  message = 'Please wait...',
  className,
}: AuthLoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-2 py-4', className)}>
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
