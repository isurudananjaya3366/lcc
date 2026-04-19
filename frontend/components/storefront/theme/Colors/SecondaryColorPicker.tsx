'use client';

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { ColorPicker } from './ColorPicker';

export function SecondaryColorPicker() {
  const { colors, updateTheme } = useTheme();
  const value = colors?.secondary ?? '#64748b';

  const handleChange = useCallback(
    (color: string) => {
      void updateTheme({ colors: { secondary: color } });
    },
    [updateTheme]
  );

  return (
    <ColorPicker
      value={value}
      onChange={handleChange}
      label="Secondary Color"
      description="Complementary color for secondary buttons, subheadings, and supporting elements."
    />
  );
}
