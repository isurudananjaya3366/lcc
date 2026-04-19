'use client';

import { useTheme } from '@/hooks/storefront/useTheme';

export function ButtonColorPreview() {
  const { colors } = useTheme();
  const primary = colors?.primary ?? '#2563eb';
  const secondary = colors?.secondary ?? '#64748b';
  const accent = colors?.accent ?? '#f59e0b';

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700">Button Preview</h4>
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          className="rounded-lg px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: primary }}
        >
          Primary Button
        </button>
        <button
          type="button"
          className="rounded-lg px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: secondary }}
        >
          Secondary Button
        </button>
        <button
          type="button"
          className="rounded-lg px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: accent }}
        >
          Accent Button
        </button>
      </div>
    </div>
  );
}
