'use client';

interface ColorSwatchProps {
  colorName: string;
  colorHex: string;
  isSelected: boolean;
  isUnavailable: boolean;
  onClick: () => void;
}

export function ColorSwatch({
  colorName,
  colorHex,
  isSelected,
  isUnavailable,
  onClick,
}: ColorSwatchProps) {
  return (
    <button
      role="radio"
      aria-checked={isSelected}
      aria-label={colorName}
      aria-disabled={isUnavailable}
      disabled={isUnavailable}
      onClick={onClick}
      className={`
        relative h-9 w-9 rounded-full border-2 transition-all
        ${isSelected ? 'border-blue-600 ring-2 ring-blue-600 ring-offset-1' : 'border-gray-300'}
        ${isUnavailable ? 'cursor-not-allowed opacity-40' : 'cursor-pointer hover:scale-110'}
      `}
      title={colorName}
    >
      <span
        className="absolute inset-0.5 rounded-full"
        style={{ backgroundColor: colorHex }}
      />
      {isUnavailable && (
        <span className="absolute inset-0 flex items-center justify-center">
          <span className="block h-full w-0.5 rotate-45 bg-red-500" />
        </span>
      )}
    </button>
  );
}
