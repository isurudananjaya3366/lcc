'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Save, Loader2, Check } from 'lucide-react';
import type { HomepageSection } from './types';

export interface SaveSectionOrderProps {
  sections: HomepageSection[];
  onSave: (sections: HomepageSection[]) => Promise<void>;
  disabled?: boolean;
}

type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export function SaveSectionOrder({ sections, onSave, disabled }: SaveSectionOrderProps) {
  const [status, setStatus] = useState<SaveStatus>('idle');

  const handleSave = async () => {
    setStatus('saving');
    try {
      await onSave(sections);
      setStatus('saved');
      setTimeout(() => setStatus('idle'), 2000);
    } catch {
      setStatus('error');
      setTimeout(() => setStatus('idle'), 3000);
    }
  };

  return (
    <Button
      onClick={handleSave}
      disabled={disabled || status === 'saving'}
      variant={status === 'error' ? 'destructive' : 'default'}
      size="sm"
    >
      {status === 'saving' && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
      {status === 'saved' && <Check className="h-4 w-4 mr-2" />}
      {status === 'idle' && <Save className="h-4 w-4 mr-2" />}
      {status === 'error' && <Save className="h-4 w-4 mr-2" />}
      {status === 'saving'
        ? 'Saving...'
        : status === 'saved'
          ? 'Saved!'
          : status === 'error'
            ? 'Error – Retry'
            : 'Save Changes'}
    </Button>
  );
}
