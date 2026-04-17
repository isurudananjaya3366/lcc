'use client';

interface SizeSelectorProps {
  sizes: string[];
  selectedSize: string | null;
  unavailableSizes: Set<string>;
  onSelect: (size: string) => void;
}

export function SizeSelector({
  sizes,
  selectedSize,
  unavailableSizes,
  onSelect,
}: SizeSelectorProps) {
  return (
    <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Size selection">
      {sizes.map((size) => {
        const isSelected = selectedSize === size;
        const isUnavailable = unavailableSizes.has(size);

        return (
          <button
            key={size}
            role="radio"
            aria-checked={isSelected}
            aria-disabled={isUnavailable}
            disabled={isUnavailable}
            onClick={() => onSelect(size)}
            className={`
              relative min-w-[3rem] rounded-md border px-3 py-2 text-sm font-medium transition-colors
              ${isSelected
                ? 'border-blue-600 bg-blue-600 text-white'
                : isUnavailable
                  ? 'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-300 line-through'
                  : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
              }
            `}
          >
            {size}
          </button>
        );
      })}
    </div>
  );
}
