'use client';

// ================================================================
// Publish Theme (Task 87)
// ================================================================
// Publishes the saved theme to the live storefront with a
// confirmation dialog before applying.
// ================================================================

import React, { useState, useCallback } from 'react';
import { Rocket, Loader2, Check } from 'lucide-react';
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
import { updateThemeApi } from '@/services/storefront/themeService';

// ─── Types ──────────────────────────────────────────────────────

export interface PublishThemeProps {
  themeId: string | null;
  isSaved: boolean;
  onPublish?: () => void;
  onSuccess?: () => void;
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────

export function PublishTheme({
  themeId,
  isSaved,
  onPublish,
  onSuccess,
  className,
}: PublishThemeProps) {
  const [isPublishing, setIsPublishing] = useState(false);
  const [isPublished, setIsPublished] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canPublish = isSaved && themeId !== null && !isPublishing;

  const handlePublish = useCallback(async () => {
    if (!themeId || isPublishing) return;

    onPublish?.();
    setIsPublishing(true);
    setError(null);

    try {
      await updateThemeApi(themeId, { isActive: true });

      setIsPublished(true);
      onSuccess?.();
      setTimeout(() => setIsPublished(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to publish theme');
    } finally {
      setIsPublishing(false);
    }
  }, [themeId, isPublishing, onPublish, onSuccess]);

  const label = isPublishing ? 'Publishing...' : isPublished ? 'Published' : 'Publish';

  const icon = isPublishing ? (
    <Loader2 className="mr-1 h-4 w-4 animate-spin" />
  ) : isPublished ? (
    <Check className="mr-1 h-4 w-4" />
  ) : (
    <Rocket className="mr-1 h-4 w-4" />
  );

  return (
    <div className={cn('flex flex-col items-start', className)}>
      <AlertDialog>
        <AlertDialogTrigger asChild>
          <Button
            variant="default"
            size="sm"
            disabled={!canPublish}
            aria-label="Publish theme"
            title="Publish theme to live store"
            className="bg-green-600 hover:bg-green-700 text-white"
          >
            {icon}
            {label}
          </Button>
        </AlertDialogTrigger>

        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Publish Theme?</AlertDialogTitle>
            <AlertDialogDescription>
              This will make your theme visible to all customers on your live store. The current
              live theme will be replaced.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handlePublish} className="bg-green-600 hover:bg-green-700">
              Publish Theme
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
    </div>
  );
}
