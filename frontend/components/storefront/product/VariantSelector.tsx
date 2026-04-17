'use client';

import { useState, useCallback } from 'react';
import type { ProductVariant } from '@/lib/api/store/modules/products';
import { VariantOptionGroup } from './VariantOptionGroup';

interface VariantSelectorProps {
  variants: ProductVariant[];
  onVariantChange?: (variant: ProductVariant | null) => void;
}

export function VariantSelector({ variants, onVariantChange }: VariantSelectorProps) {
  // Extract unique attribute names and their values
  const attributeMap = new Map<string, Set<string>>();
  for (const variant of variants) {
    for (const [key, value] of Object.entries(variant.attributes)) {
      if (!attributeMap.has(key)) attributeMap.set(key, new Set());
      attributeMap.get(key)!.add(value);
    }
  }

  const [selectedAttributes, setSelectedAttributes] = useState<Record<string, string>>({});

  const handleSelect = useCallback(
    (attributeName: string, value: string) => {
      const updated = { ...selectedAttributes, [attributeName]: value };
      setSelectedAttributes(updated);

      // Find matching variant
      const match = variants.find((v) =>
        Object.entries(updated).every(([k, val]) => v.attributes[k] === val)
      );
      onVariantChange?.(match ?? null);
    },
    [selectedAttributes, variants, onVariantChange]
  );

  // Determine which values are unavailable based on current selections
  const getUnavailableValues = useCallback(
    (attributeName: string): Set<string> => {
      const unavailable = new Set<string>();
      const otherSelections = Object.entries(selectedAttributes).filter(
        ([k]) => k !== attributeName
      );

      if (otherSelections.length === 0) return unavailable;

      const values = attributeMap.get(attributeName) ?? new Set();
      for (const value of values) {
        const testAttrs = { ...Object.fromEntries(otherSelections), [attributeName]: value };
        const match = variants.find(
          (v) =>
            Object.entries(testAttrs).every(([k, val]) => v.attributes[k] === val) && v.in_stock
        );
        if (!match) unavailable.add(value);
      }

      return unavailable;
    },
    [selectedAttributes, variants, attributeMap]
  );

  if (attributeMap.size === 0) return null;

  return (
    <div className="space-y-4">
      {Array.from(attributeMap.entries()).map(([name, values]) => (
        <VariantOptionGroup
          key={name}
          name={name}
          values={Array.from(values)}
          selectedValue={selectedAttributes[name] ?? null}
          unavailableValues={getUnavailableValues(name)}
          onSelect={(value) => handleSelect(name, value)}
        />
      ))}
    </div>
  );
}
