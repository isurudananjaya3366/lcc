'use client';

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { ColorPicker } from './ColorPicker';

export function BackgroundColor() {
  const { colors, updateTheme } = useTheme();
  const value = colors?.background ?? '#ffffff';

  const handleChange = useCallback(
    (color: string) => {
      void updateTheme({ colors: { background: color } });
    },
    [updateTheme]
  );

  return (
    <ColorPicker
      value={value}
      onChange={handleChange}
      label="Background Color"
      description="Main page background color. Light colors recommended for readability."
    />
  );
}
