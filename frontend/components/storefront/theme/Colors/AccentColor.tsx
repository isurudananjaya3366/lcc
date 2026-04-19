'use client';

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { ColorPicker } from './ColorPicker';

export function AccentColor() {
  const { colors, updateTheme } = useTheme();
  const value = colors?.accent ?? '#f59e0b';

  const handleChange = useCallback(
    (color: string) => {
      void updateTheme({ colors: { accent: color } });
    },
    [updateTheme]
  );

  return (
    <ColorPicker
      value={value}
      onChange={handleChange}
      label="Accent Color"
      description="Used for call-to-action buttons, links, badges, and highlights."
    />
  );
}
