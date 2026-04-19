'use client';

// ================================================================
// Draft Mode (Task 88)
// ================================================================
// Displays draft/published status badge and provides save-as-draft
// functionality with last-saved timestamp.
// ================================================================

import React, { useMemo } from 'react';
import { FileEdit, CheckCircle, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

// ─── Types ──────────────────────────────────────────────────────

export interface DraftModeProps {
  status: 'draft' | 'published';
  lastSaved: Date | null;
  onSaveAsDraft?: () => void;
  className?: string;
}

// ─── Helpers ────────────────────────────────────────────────────

function formatRelativeTime(date: Date): string {
  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) return 'Just now';
  if (diffMinutes < 60) return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays <= 6) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

  return date.toLocaleDateString();
}

// ─── Component ──────────────────────────────────────────────────

export function DraftMode({ status, lastSaved, onSaveAsDraft, className }: DraftModeProps) {
  const timeAgo = useMemo(() => (lastSaved ? formatRelativeTime(lastSaved) : null), [lastSaved]);

  const isDraft = status === 'draft';

  return (
    <div className={cn('flex items-center gap-3 text-sm', className)}>
      {/* Status badge */}
      <Badge
        variant={isDraft ? 'secondary' : 'default'}
        className={cn(
          'gap-1',
          isDraft
            ? 'bg-muted text-muted-foreground'
            : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
        )}
      >
        {isDraft ? <FileEdit className="h-3 w-3" /> : <CheckCircle className="h-3 w-3" />}
        {isDraft ? 'Draft' : 'Published'}
      </Badge>

      {/* Last saved timestamp */}
      {timeAgo && <span className="text-xs text-muted-foreground">Last saved: {timeAgo}</span>}

      {!lastSaved && (
        <span className="flex items-center gap-1 text-xs text-orange-600 dark:text-orange-400">
          <AlertCircle className="h-3 w-3" />
          Unsaved changes
        </span>
      )}

      {/* Save as Draft button */}
      {onSaveAsDraft && status === 'published' && (
        <Button variant="ghost" size="sm" onClick={onSaveAsDraft} className="ml-auto text-xs">
          <FileEdit className="mr-1 h-3 w-3" />
          Save as Draft
        </Button>
      )}
    </div>
  );
}
