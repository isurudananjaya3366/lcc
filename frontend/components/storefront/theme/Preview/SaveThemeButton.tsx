'use client';

// ================================================================
// Save Theme Button (Task 86)
// ================================================================
// Saves current theme configuration to the database via API.
// ================================================================

import React, { useState, useCallback } from 'react';
import { Save, Check, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/storefront/useTheme';
import { updateThemeApi } from '@/services/storefront/themeService';

// ─── Types ──────────────────────────────────────────────────────

export interface SaveThemeButtonProps {
  hasChanges: boolean;
  onSave?: () => void;
  onSuccess?: () => void;
  className?: string;
}

// ─── Component ──────────────────────────────────────────────────

export function SaveThemeButton({
  hasChanges,
  onSave,
  onSuccess,
  className,
}: SaveThemeButtonProps) {
  const { theme } = useTheme();
  const [isSaving, setIsSaving] = useState(false);
  const [showSaved, setShowSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = useCallback(async () => {
    if (!theme || isSaving) return;

    onSave?.();
    setIsSaving(true);
    setError(null);

    try {
      await updateThemeApi(theme.id, {
        colors: theme.colors,
        fonts: theme.fonts,
        logo: theme.logo,
        homepage: theme.homepage,
        name: theme.name,
      });

      setShowSaved(true);
      onSuccess?.();
      setTimeout(() => setShowSaved(false), 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save theme');
    } finally {
      setIsSaving(false);
    }
  }, [theme, isSaving, onSave, onSuccess]);

  const label = isSaving ? 'Saving...' : showSaved ? 'Saved' : hasChanges ? 'Save' : 'Saved';

  const icon = isSaving ? (
    <Loader2 className="mr-1 h-4 w-4 animate-spin" />
  ) : showSaved ? (
    <Check className="mr-1 h-4 w-4" />
  ) : (
    <Save className="mr-1 h-4 w-4" />
  );

  return (
    <div className={cn('flex flex-col items-start', className)}>
      <Button
        variant={hasChanges ? 'default' : 'outline'}
        size="sm"
        onClick={handleSave}
        disabled={!hasChanges || isSaving}
        aria-label="Save theme changes"
        title="Save Theme (Ctrl+S)"
      >
        {icon}
        {label}
      </Button>
      {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
    </div>
  );
}
