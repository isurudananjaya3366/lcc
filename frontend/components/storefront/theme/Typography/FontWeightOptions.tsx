'use client';

// ================================================================
// Font Weight Options – Weight selection for headings & body
// ================================================================

import { useCallback } from 'react';

interface FontWeightOptionsProps {
  headingWeight: number;
  bodyWeight: number;
  onHeadingWeightChange: (weight: number) => void;
  onBodyWeightChange: (weight: number) => void;
  availableWeights?: number[];
  className?: string;
}

const WEIGHT_OPTIONS = [
  { value: 400, label: 'Regular' },
  { value: 500, label: 'Medium' },
  { value: 600, label: 'Semi-bold' },
  { value: 700, label: 'Bold' },
] as const;

export function FontWeightOptions({
  headingWeight,
  bodyWeight,
  onHeadingWeightChange,
  onBodyWeightChange,
  availableWeights,
  className,
}: FontWeightOptionsProps) {
  const weights = availableWeights ?? WEIGHT_OPTIONS.map((w) => w.value);
  const options = WEIGHT_OPTIONS.filter((w) => weights.includes(w.value));

  const hierarchyWarning = headingWeight > 0 && bodyWeight > 0 && headingWeight <= bodyWeight;

  const handleHeading = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onHeadingWeightChange(Number(e.target.value));
    },
    [onHeadingWeightChange]
  );

  const handleBody = useCallback(
    (e: React.ChangeEvent<HTMLSelectElement>) => {
      onBodyWeightChange(Number(e.target.value));
    },
    [onBodyWeightChange]
  );

  return (
    <div className={`space-y-4 ${className ?? ''}`}>
      <h4 className="text-sm font-medium text-gray-700">Font Weights</h4>

      {/* Heading weight */}
      <div className="space-y-1.5">
        <label htmlFor="heading-weight" className="block text-xs font-medium text-gray-600">
          Heading Weight
        </label>
        <select
          id="heading-weight"
          value={headingWeight}
          onChange={handleHeading}
          className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {options.map((w) => (
            <option key={w.value} value={w.value}>
              {w.label} ({w.value})
            </option>
          ))}
        </select>
        <p className="text-sm text-gray-800" style={{ fontWeight: headingWeight }}>
          Sample Heading Text
        </p>
      </div>

      {/* Body weight */}
      <div className="space-y-1.5">
        <label htmlFor="body-weight" className="block text-xs font-medium text-gray-600">
          Body Weight
        </label>
        <select
          id="body-weight"
          value={bodyWeight}
          onChange={handleBody}
          className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          {options.map((w) => (
            <option key={w.value} value={w.value}>
              {w.label} ({w.value})
            </option>
          ))}
        </select>
        <p className="text-sm text-gray-600" style={{ fontWeight: bodyWeight }}>
          Sample body text paragraph
        </p>
      </div>

      {hierarchyWarning && (
        <p className="rounded bg-amber-50 px-3 py-2 text-xs text-amber-700">
          Heading weight should be heavier than body weight for visual hierarchy.
        </p>
      )}
    </div>
  );
}
