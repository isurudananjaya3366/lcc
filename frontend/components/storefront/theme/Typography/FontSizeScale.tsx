'use client';

// ================================================================
// Font Size Scale – Base font size slider / input
// ================================================================

import { useCallback } from 'react';

interface FontSizeScaleProps {
  value: number;
  onChange: (size: number) => void;
  showPreview?: boolean;
  className?: string;
}

const SIZE_OPTIONS = [
  { label: 'Small', value: 14, multiplier: 0.875 },
  { label: 'Medium', value: 16, multiplier: 1.0, recommended: true },
  { label: 'Large', value: 18, multiplier: 1.125 },
  { label: 'Extra Large', value: 20, multiplier: 1.25 },
] as const;

export function FontSizeScale({
  value,
  onChange,
  showPreview = true,
  className,
}: FontSizeScaleProps) {
  const handleChange = useCallback(
    (size: number) => {
      onChange(size);
    },
    [onChange]
  );

  return (
    <div className={`space-y-3 ${className ?? ''}`}>
      <div>
        <h4 className="text-sm font-medium text-gray-700">Base Font Size</h4>
        <p className="text-xs text-gray-500">Adjust the base text size for the entire store</p>
      </div>

      <div className="space-y-2">
        {SIZE_OPTIONS.map((opt) => {
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
                name="fontSize"
                checked={selected}
                onChange={() => handleChange(opt.value)}
                className="h-4 w-4 text-blue-600"
              />
              <div className="flex-1">
                <span className="text-sm font-medium text-gray-900">
                  {opt.label} ({opt.value}px)
                </span>
                {'recommended' in opt && opt.recommended && (
                  <span className="ml-2 rounded bg-blue-100 px-1.5 py-0.5 text-[10px] font-medium text-blue-700">
                    Recommended
                  </span>
                )}
                {showPreview && (
                  <p className="mt-1 text-gray-600" style={{ fontSize: `${opt.value}px` }}>
                    Sample text at {opt.value}px
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
