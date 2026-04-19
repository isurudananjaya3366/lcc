'use client';

export interface LogoSizeControlProps {
  value: number;
  onChange: (size: number) => void;
  min?: number;
  max?: number;
  step?: number;
  disabled?: boolean;
}

const PRESETS = [
  { label: 'S', size: 40 },
  { label: 'M', size: 60 },
  { label: 'L', size: 80 },
  { label: 'XL', size: 100 },
] as const;

export function LogoSizeControl({
  value,
  onChange,
  min = 40,
  max = 100,
  step = 5,
  disabled = false,
}: LogoSizeControlProps) {
  const clamp = (v: number) => Math.min(max, Math.max(min, v));

  const handleSlider = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(clamp(Number(e.target.value)));
  };

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const num = parseInt(e.target.value, 10);
    if (!isNaN(num)) onChange(clamp(num));
  };

  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-gray-700">Logo Size</p>

      {/* Presets */}
      <div className="flex gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.label}
            type="button"
            disabled={disabled}
            onClick={() => onChange(p.size)}
            className={`rounded-md border px-3 py-1 text-sm font-medium transition-colors ${
              value === p.size
                ? 'border-blue-600 bg-blue-50 text-blue-700'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            } disabled:opacity-50`}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Slider */}
      <div className="flex items-center gap-3">
        <span className="text-xs text-gray-400">{min}</span>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={handleSlider}
          disabled={disabled}
          className="flex-1 accent-blue-600"
        />
        <span className="text-xs text-gray-400">{max}</span>
      </div>

      {/* Number input */}
      <div className="flex items-center gap-2">
        <label className="text-sm text-gray-600">Height:</label>
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={handleInput}
          disabled={disabled}
          className="w-20 rounded-md border border-gray-300 px-2 py-1 text-sm disabled:opacity-50"
        />
        <span className="text-sm text-gray-500">px</span>
      </div>
    </div>
  );
}
