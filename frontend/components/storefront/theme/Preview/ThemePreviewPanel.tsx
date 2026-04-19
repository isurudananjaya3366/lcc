'use client';

// ================================================================
// Theme Preview Panel (Task 81)
// ================================================================
// Main container for the live theme preview system with viewport
// toggle, action buttons, and preview frame.
// ================================================================

import React, { useState, useCallback } from 'react';
import { X, Monitor, Smartphone } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { PreviewFrame } from './PreviewFrame';
import { PreviewRefresh } from './PreviewRefresh';
import { SaveThemeButton } from './SaveThemeButton';
import { PublishTheme } from './PublishTheme';
import { DraftMode } from './DraftMode';
import { UndoChanges } from './UndoChanges';
import { useTheme } from '@/hooks/storefront/useTheme';

// ─── Types ──────────────────────────────────────────────────────

export type Viewport = 'desktop' | 'mobile';
export type PanelPosition = 'right' | 'modal';

export interface ThemePreviewPanelProps {
  isOpen: boolean;
  onClose?: () => void;
  className?: string;
  position?: PanelPosition;
}

// ─── Component ──────────────────────────────────────────────────

export function ThemePreviewPanel({
  isOpen,
  onClose,
  className,
  position = 'right',
}: ThemePreviewPanelProps) {
  const { theme } = useTheme();
  const [viewport, setViewport] = useState<Viewport>('desktop');
  const [isLoading, setIsLoading] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  const [status, setStatus] = useState<'draft' | 'published'>('draft');

  const handleRefresh = useCallback(() => {
    setIsLoading(true);
    setRefreshKey((k) => k + 1);
    setTimeout(() => setIsLoading(false), 1000);
  }, []);

  const handleSaveSuccess = useCallback(() => {
    setLastSaved(new Date());
    setHasChanges(false);
  }, []);

  const handlePublishSuccess = useCallback(() => {
    setStatus('published');
    setLastSaved(new Date());
    setHasChanges(false);
  }, []);

  const handleUndo = useCallback(() => {
    setHasChanges(false);
  }, []);

  const handleSaveAsDraft = useCallback(() => {
    setStatus('draft');
    setLastSaved(new Date());
    setHasChanges(false);
  }, []);

  if (!isOpen) return null;

  const isModal = position === 'modal';

  return (
    <div
      className={cn(
        'flex flex-col bg-background border-l border-border',
        isModal
          ? 'fixed inset-0 z-50 bg-background/80 backdrop-blur-sm'
          : 'relative h-full w-full lg:w-1/2',
        className
      )}
    >
      {/* ── Header ── */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold">Theme Preview</h2>
        {onClose && (
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close preview panel">
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* ── Toolbar ── */}
      <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-2">
        {/* Viewport Toggle */}
        <div className="flex items-center rounded-md border border-border">
          <Button
            variant={viewport === 'desktop' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setViewport('desktop')}
            aria-label="Desktop preview"
          >
            <Monitor className="mr-1 h-4 w-4" />
            Desktop
          </Button>
          <Button
            variant={viewport === 'mobile' ? 'secondary' : 'ghost'}
            size="sm"
            onClick={() => setViewport('mobile')}
            aria-label="Mobile preview"
          >
            <Smartphone className="mr-1 h-4 w-4" />
            Mobile
          </Button>
        </div>

        <PreviewRefresh onRefresh={handleRefresh} loading={isLoading} />

        <div className="ml-auto flex items-center gap-2">
          <SaveThemeButton hasChanges={hasChanges} onSuccess={handleSaveSuccess} />
          <PublishTheme
            themeId={theme?.id ?? null}
            isSaved={!hasChanges && lastSaved !== null}
            onSuccess={handlePublishSuccess}
          />
          <UndoChanges hasChanges={hasChanges} onUndo={handleUndo} />
        </div>
      </div>

      {/* ── Preview Area ── */}
      <div className="flex-1 overflow-auto bg-muted/30 p-4">
        <PreviewFrame key={refreshKey} viewport={viewport} />
      </div>

      {/* ── Footer ── */}
      <div className="border-t border-border px-4 py-2">
        <DraftMode status={status} lastSaved={lastSaved} onSaveAsDraft={handleSaveAsDraft} />
      </div>
    </div>
  );
}
