'use client';

import { ColorSwatch } from './ColorSwatch';

interface ColorSelectorProps {
  colors: string[];
  selectedColor: string | null;
  unavailableColors: Set<string>;
  onSelect: (color: string) => void;
}

// Map common color names to CSS values
const COLOR_MAP: Record<string, string> = {
  red: '#EF4444',
  blue: '#3B82F6',
  green: '#22C55E',
  black: '#111827',
  white: '#FFFFFF',
  yellow: '#EAB308',
  orange: '#F97316',
  purple: '#A855F7',
  pink: '#EC4899',
  brown: '#92400E',
  gray: '#6B7280',
  grey: '#6B7280',
  navy: '#1E3A5F',
  beige: '#F5F5DC',
  maroon: '#800000',
  teal: '#14B8A6',
};

function getColorHex(colorName: string): string {
  return COLOR_MAP[colorName.toLowerCase()] ?? '#9CA3AF';
}

export function ColorSelector({
  colors,
  selectedColor,
  unavailableColors,
  onSelect,
}: ColorSelectorProps) {
  return (
    <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Color selection">
      {colors.map((color) => (
        <ColorSwatch
          key={color}
          colorName={color}
          colorHex={getColorHex(color)}
          isSelected={selectedColor === color}
          isUnavailable={unavailableColors.has(color)}
          onClick={() => onSelect(color)}
        />
      ))}
    </div>
  );
}
