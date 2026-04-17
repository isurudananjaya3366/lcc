'use client';

import { SizeSelector } from './SizeSelector';
import { ColorSelector } from './ColorSelector';

interface VariantOptionGroupProps {
  name: string;
  values: string[];
  selectedValue: string | null;
  unavailableValues: Set<string>;
  onSelect: (value: string) => void;
}

export function VariantOptionGroup({
  name,
  values,
  selectedValue,
  unavailableValues,
  onSelect,
}: VariantOptionGroupProps) {
  const lowerName = name.toLowerCase();

  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-gray-900">
        {name}
        {selectedValue && (
          <span className="ml-2 text-gray-500">: {selectedValue}</span>
        )}
      </label>
      {lowerName === 'color' || lowerName === 'colour' ? (
        <ColorSelector
          colors={values}
          selectedColor={selectedValue}
          unavailableColors={unavailableValues}
          onSelect={onSelect}
        />
      ) : (
        <SizeSelector
          sizes={values}
          selectedSize={selectedValue}
          unavailableSizes={unavailableValues}
          onSelect={onSelect}
        />
      )}
    </div>
  );
}
