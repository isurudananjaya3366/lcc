'use client';

import { useCallback } from 'react';
import { cn } from '@/lib/utils';

interface SizeFilterProps {
  sizes: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

export function SizeFilter({ sizes, selected, onChange }: SizeFilterProps) {
  const toggle = useCallback(
    (size: string) => {
      const isSelected = selected.includes(size);
      onChange(isSelected ? selected.filter((s) => s !== size) : [...selected, size]);
    },
    [selected, onChange]
  );

  if (!sizes.length) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {sizes.map((size) => {
        const isSelected = selected.includes(size);
        return (
          <button
            key={size}
            type="button"
            onClick={() => toggle(size)}
            aria-pressed={isSelected}
            className={cn(
              'min-w-[40px] h-10 px-3 border rounded-md text-sm font-medium transition-colors duration-150 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-1',
              isSelected
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-900 border-gray-300 hover:border-blue-300'
            )}
          >
            {size}
          </button>
        );
      })}
    </div>
  );
}
