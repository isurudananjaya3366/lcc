'use client';

import { useCallback } from 'react';
import type { StoreProductAttribute } from '@/types/store/product';
import { FilterSection } from './FilterSection';

interface AttributeFilterProps {
  attributes: StoreProductAttribute[];
  selected: Record<string, string[]>;
  onChange: (selected: Record<string, string[]>) => void;
}

export function AttributeFilter({ attributes, selected, onChange }: AttributeFilterProps) {
  const toggleValue = useCallback(
    (attrName: string, value: string) => {
      const current = selected[attrName] ?? [];
      const isSelected = current.includes(value);
      const updated = isSelected ? current.filter((v) => v !== value) : [...current, value];

      const next = { ...selected };
      if (updated.length === 0) {
        delete next[attrName];
      } else {
        next[attrName] = updated;
      }
      onChange(next);
    },
    [selected, onChange]
  );

  if (!attributes.length) return null;

  return (
    <div className="space-y-0">
      {attributes.map((attr) => {
        const selectedValues = selected[attr.name] ?? [];
        return (
          <FilterSection
            key={attr.name}
            title={attr.name}
            badge={selectedValues.length || undefined}
            defaultOpen={false}
            className="border-b-0 py-2"
          >
            <div className="space-y-1.5">
              {attr.values.map((value) => (
                <label
                  key={value}
                  className="flex items-center gap-2 cursor-pointer text-sm text-gray-700 hover:text-gray-900 select-none py-0.5"
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(value)}
                    onChange={() => toggleValue(attr.name, value)}
                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span>{value}</span>
                </label>
              ))}
            </div>
          </FilterSection>
        );
      })}
    </div>
  );
}
