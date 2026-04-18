'use client';

import { Facebook, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/cn';

export interface FacebookButtonProps {
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
}

export function FacebookButton({ onClick, disabled = true, loading = false }: FacebookButtonProps) {
  return (
    <div className="relative group">
      <Button
        className={cn(
          'w-full bg-[#1877F2] hover:bg-[#166FE5] text-white border-transparent',
          disabled && 'opacity-60 cursor-not-allowed'
        )}
        disabled={disabled || loading}
        onClick={onClick}
        type="button"
        data-testid="social-facebook"
      >
        {loading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Facebook className="mr-2 h-4 w-4" />
        )}
        Continue with Facebook
      </Button>
      {disabled && !loading && (
        <span className="absolute -top-8 left-1/2 -translate-x-1/2 rounded bg-gray-900 px-2 py-1 text-xs text-white opacity-0 transition-opacity group-hover:opacity-100 pointer-events-none whitespace-nowrap">
          Coming soon
        </span>
      )}
    </div>
  );
}
