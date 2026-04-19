'use client';

// ================================================================
// Line Height Setting – Line height configuration
// ================================================================

import { useCallback } from 'react';

interface LineHeightSettingProps {
  value: number;
  onChange: (lineHeight: number) => void;
  showPreview?: boolean;
  className?: string;
}

const LINE_HEIGHT_OPTIONS = [
  { label: 'Tight', value: 1.25 },
  { label: 'Normal', value: 1.5, recommended: true },
  { label: 'Relaxed', value: 1.75 },
  { label: 'Loose', value: 2.0 },
] as const;

const SAMPLE_TEXT =
  'This is a sample paragraph demonstrating line height. Proper spacing improves readability and visual comfort.';

export function LineHeightSetting({
  value,
  onChange,
  showPreview = true,
  className,
}: LineHeightSettingProps) {
  const handleChange = useCallback(
    (lh: number) => {
      onChange(lh);
    },
    [onChange]
  );

  return (
    <div className={`space-y-3 ${className ?? ''}`}>
      <div>
        <h4 className="text-sm font-medium text-gray-700">Line Height</h4>
        <p className="text-xs text-gray-500">Control spacing between lines of text</p>
      </div>

      <div className="space-y-2">
        {LINE_HEIGHT_OPTIONS.map((opt) => {
          const selected = value === opt.value;
          return (
            <label
              key={opt.value}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
                selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="lineHeight"
                checked={selected}
                onChange={() => handleChange(opt.value)}
                className="h-4 w-4 text-blue-600"
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-900">
                  {opt.label} ({opt.value})
                </span>
                {'recommended' in opt && opt.recommended && (
                  <span className="ml-2 rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700">
                    Recommended
                  </span>
                )}
                {showPreview && (
                  <p className="mt-1 text-xs text-gray-600" style={{ lineHeight: opt.value }}>
                    {SAMPLE_TEXT}
                  </p>
                )}
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
}
