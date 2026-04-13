'use client';

import * as React from 'react';
import { Loader2, Save, Trash2, RefreshCw } from 'lucide-react';
import { Button, type ButtonProps } from '@/components/ui/button';
import { cn } from '@/lib/utils';

// ================================================================
// Helper Button Components — Pre-configured for common ERP actions
// ================================================================

// --- SaveButton ---
export interface SaveButtonProps extends Omit<ButtonProps, 'variant'> {
  saving?: boolean;
  savedText?: string;
}

export function SaveButton({
  saving = false,
  savedText,
  children = 'Save',
  className,
  ...props
}: SaveButtonProps) {
  return (
    <Button
      variant="default"
      loading={saving}
      icon={!saving ? <Save className="size-4" /> : undefined}
      className={className}
      {...props}
    >
      {saving ? 'Saving…' : savedText ?? children}
    </Button>
  );
}

// --- DeleteButton ---
export interface DeleteButtonProps extends Omit<ButtonProps, 'variant'> {
  deleting?: boolean;
}

export function DeleteButton({
  deleting = false,
  children = 'Delete',
  className,
  ...props
}: DeleteButtonProps) {
  return (
    <Button
      variant="destructive"
      loading={deleting}
      icon={!deleting ? <Trash2 className="size-4" /> : undefined}
      className={className}
      {...props}
    >
      {deleting ? 'Deleting…' : children}
    </Button>
  );
}

// --- RefreshButton ---
export interface RefreshButtonProps extends Omit<ButtonProps, 'variant' | 'size'> {
  refreshing?: boolean;
}

export function RefreshButton({
  refreshing = false,
  className,
  ...props
}: RefreshButtonProps) {
  return (
    <Button
      variant="outline"
      size="icon"
      disabled={refreshing}
      className={className}
      aria-label="Refresh"
      {...props}
    >
      <RefreshCw className={cn('size-4', refreshing && 'animate-spin')} />
    </Button>
  );
}

// --- ActionButton ---
export interface ActionButtonProps extends ButtonProps {
  /** Shows loading spinner and disables the button */
  processing?: boolean;
}

export function ActionButton({
  processing = false,
  children,
  ...props
}: ActionButtonProps) {
  return (
    <Button loading={processing} {...props}>
      {children}
    </Button>
  );
}
