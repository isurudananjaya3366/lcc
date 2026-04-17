'use client';

import { useCallback } from 'react';
import { cn } from '@/lib/utils';

interface ColorFilterProps {
  colors: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

const COLOR_MAP: Record<string, string> = {
  red: '#EF4444',
  blue: '#3B82F6',
  green: '#22C55E',
  black: '#000000',
  white: '#FFFFFF',
  yellow: '#EAB308',
  purple: '#A855F7',
  pink: '#EC4899',
  orange: '#F97316',
  gray: '#6B7280',
  grey: '#6B7280',
  brown: '#92400E',
  navy: '#1E3A5F',
  beige: '#F5F5DC',
  teal: '#14B8A6',
  maroon: '#7F1D1D',
};

function getHex(color: string): string {
  return COLOR_MAP[color.toLowerCase()] ?? '#9CA3AF';
}

function isLight(hex: string): boolean {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 > 180;
}

export function ColorFilter({ colors, selected, onChange }: ColorFilterProps) {
  const toggle = useCallback(
    (color: string) => {
      const isSelected = selected.includes(color);
      onChange(isSelected ? selected.filter((c) => c !== color) : [...selected, color]);
    },
    [selected, onChange]
  );

  if (!colors.length) return null;

  return (
    <div className="grid grid-cols-5 gap-3">
      {colors.map((color) => {
        const hex = getHex(color);
        const isChecked = selected.includes(color);
        const light = isLight(hex);

        return (
          <div key={color} className="flex flex-col items-center gap-1">
            <button
              type="button"
              onClick={() => toggle(color)}
              aria-label={`${color}${isChecked ? ', selected' : ''}`}
              aria-pressed={isChecked}
              className={cn(
                'relative h-8 w-8 rounded-full border transition-all duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
                isChecked ? 'ring-2 ring-blue-500 ring-offset-2' : 'hover:scale-110',
                light ? 'border-gray-300' : 'border-transparent'
              )}
              style={{ backgroundColor: hex }}
            >
              {isChecked && (
                <svg
                  className={cn(
                    'absolute inset-0 m-auto h-4 w-4',
                    light ? 'text-gray-900' : 'text-white'
                  )}
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z"
                    clipRule="evenodd"
                  />
                </svg>
              )}
            </button>
            <span className="text-xs text-gray-500 capitalize truncate w-full text-center">
              {color}
            </span>
          </div>
        );
      })}
    </div>
  );
}
