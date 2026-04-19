'use client';

import { useTheme } from '@/hooks/storefront/useTheme';

export function LinkColorPreview() {
  const { colors } = useTheme();
  const accent = colors?.accent ?? '#f59e0b';
  const primary = colors?.primary ?? '#2563eb';
  const textColor = colors?.text.primary ?? '#0f172a';

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700">Link Preview</h4>
      <div className="space-y-2 text-sm" style={{ color: textColor }}>
        <p>
          This is paragraph text with an{' '}
          <span className="cursor-pointer underline hover:opacity-80" style={{ color: accent }}>
            accent link
          </span>{' '}
          inline.
        </p>
        <p>
          And here is a{' '}
          <span className="cursor-pointer underline hover:opacity-80" style={{ color: primary }}>
            primary link
          </span>{' '}
          for navigation.
        </p>
      </div>
    </div>
  );
}
