'use client';

import * as React from 'react';
import { Check, Copy } from 'lucide-react';
import { cn } from '@/lib/utils';

// ================================================================
// CopyButton — Copy text to clipboard with visual feedback
// ================================================================

export interface CopyButtonProps {
  value: string;
  onCopy?: () => void;
  label?: string;
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const sizeClasses = {
  sm: 'h-7 px-2 text-xs',
  md: 'h-8 px-3 text-sm',
  lg: 'h-9 px-4 text-sm',
} as const;

const iconSizeClasses = {
  sm: 'size-3',
  md: 'size-3.5',
  lg: 'size-4',
} as const;

export function CopyButton({
  value,
  onCopy,
  label = 'Copy',
  showLabel = true,
  size = 'md',
  className,
}: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = React.useCallback(async () => {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      onCopy?.();
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = value;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        onCopy?.();
        setTimeout(() => setCopied(false), 2000);
      } finally {
        document.body.removeChild(textarea);
      }
    }
  }, [value, onCopy]);

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={cn(
        'inline-flex items-center justify-center gap-1.5 rounded-md border border-input bg-background font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
        sizeClasses[size],
        className,
      )}
      aria-label={copied ? 'Copied' : label}
    >
      {copied ? (
        <>
          <Check className={cn(iconSizeClasses[size], 'text-green-600')} />
          {showLabel && <span aria-live="polite">Copied!</span>}
        </>
      ) : (
        <>
          <Copy className={iconSizeClasses[size]} />
          {showLabel && <span>{label}</span>}
        </>
      )}
    </button>
  );
}
