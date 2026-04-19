'use client';

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { ColorPicker } from './ColorPicker';

export function PrimaryColorPicker() {
  const { colors, updateTheme } = useTheme();
  const value = colors?.primary ?? '#2563eb';

  const handleChange = useCallback(
    (color: string) => {
      void updateTheme({ colors: { primary: color } });
    },
    [updateTheme]
  );

  return (
    <ColorPicker
      value={value}
      onChange={handleChange}
      label="Primary Color"
      description="Main brand color used for headers, primary buttons, and key brand elements."
    />
  );
}
