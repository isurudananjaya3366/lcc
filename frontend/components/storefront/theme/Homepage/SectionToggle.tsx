'use client';

import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

export interface SectionToggleProps {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  disabled?: boolean;
  label?: string;
  size?: 'sm' | 'md';
}

export function SectionToggle({
  enabled,
  onChange,
  disabled = false,
  label,
  size = 'md',
}: SectionToggleProps) {
  const id = React.useId();

  return (
    <div className={cn('flex items-center gap-2', size === 'sm' && 'scale-90')}>
      <Switch
        id={id}
        checked={enabled}
        onCheckedChange={onChange}
        disabled={disabled}
        aria-label={label ?? (enabled ? 'Disable section' : 'Enable section')}
      />
      {label && (
        <Label htmlFor={id} className="text-sm text-muted-foreground cursor-pointer">
          {label}
        </Label>
      )}
    </div>
  );
}
