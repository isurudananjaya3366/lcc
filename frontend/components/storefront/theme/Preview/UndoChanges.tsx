'use client';

// ================================================================
// Undo Changes (Task 89)
// ================================================================
// Restores the last saved theme state from the store, with a
// confirmation dialog for undoing all unsaved changes.
// ================================================================

import React, { useState, useCallback } from 'react';
import { Undo2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useTheme } from '@/hooks/storefront/useTheme';

// ─── Types ──────────────────────────────────────────────────────

export interface UndoChangesProps {
  hasChanges: boolean;
  onUndo: () => void;
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────

export function UndoChanges({ hasChanges, onUndo, className }: UndoChangesProps) {
  const { resetTheme } = useTheme();

  const handleUndo = useCallback(async () => {
    try {
      await resetTheme();
      onUndo();
    } catch {
      // Reset failed – state unchanged
    }
  }, [resetTheme, onUndo]);

  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          disabled={!hasChanges}
          aria-label="Undo changes"
          title="Undo all unsaved changes"
          className={cn(className)}
        >
          <Undo2 className="mr-1 h-4 w-4" />
          Undo
        </Button>
      </AlertDialogTrigger>

      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Undo All Changes?</AlertDialogTitle>
          <AlertDialogDescription>
            This will revert all unsaved changes and restore the last saved theme state. This action
            cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleUndo}>Undo Changes</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
