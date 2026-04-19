'use client';

import { useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { ColorPicker } from './ColorPicker';
import { getContrastRatio, getWCAGLevel } from './ContrastCheck';

export function TextColor() {
  const { colors, updateTheme } = useTheme();
  const textColor = colors?.text.primary ?? '#0f172a';
  const bgColor = colors?.background ?? '#ffffff';

  const ratio = getContrastRatio(textColor, bgColor);
  const level = getWCAGLevel(ratio);

  const handleChange = useCallback(
    (color: string) => {
      void updateTheme({ colors: { text: { primary: color } } });
    },
    [updateTheme]
  );

  return (
    <div className="space-y-2">
      <ColorPicker
        value={textColor}
        onChange={handleChange}
        label="Text Color"
        description="Main body text color throughout the site."
      />
      <div className="flex items-center gap-2 text-xs">
        <span className="text-gray-500">Contrast with background:</span>
        <span
          className={
            level === 'Fail'
              ? 'font-semibold text-red-600'
              : level === 'AA-Large'
                ? 'font-semibold text-yellow-600'
                : 'font-semibold text-green-600'
          }
        >
          {ratio.toFixed(1)}:1 — {level}
        </span>
      </div>
      <div
        className="rounded border p-3 text-sm"
        style={{ backgroundColor: bgColor, color: textColor }}
      >
        <p className="font-semibold">Heading Example</p>
        <p>This is sample body text demonstrating the text color on the selected background.</p>
      </div>
    </div>
  );
}
