'use client';

import { Chrome, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/cn';

export interface GoogleButtonProps {
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export function GoogleButton({ onClick, disabled = true, loading = false }: GoogleButtonProps) {
  return (
    <div className="relative group">
      <Button
        variant="outline"
        className={cn(
          'w-full bg-white hover:bg-gray-50 text-gray-700 border-gray-300',
          disabled && 'opacity-60 cursor-not-allowed'
        )}
        disabled={disabled || loading}
        onClick={onClick}
        type="button"
        data-testid="social-google"
      >
        {loading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Chrome className="mr-2 h-4 w-4" />
        )}
        Continue with Google
      </Button>
      {disabled && !loading && (
        <span className="absolute -top-8 left-1/2 -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100 pointer-events-none whitespace-nowrap">
          Coming soon
        </span>
      )}
    </div>
  );
}
