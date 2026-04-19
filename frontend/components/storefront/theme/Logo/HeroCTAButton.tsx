'use client';

export interface HeroCTAButtonProps {
  text: string;
  link: string;
  style: 'primary' | 'secondary' | 'outline';
  onChange: (
    updates: Partial<{
      ctaText: string;
      ctaLink: string;
      ctaStyle: 'primary' | 'secondary' | 'outline';
    }>
  ) => void;
}

const STYLE_OPTIONS = [
  { value: 'primary' as const, label: 'Primary', className: 'bg-blue-600 text-white' },
  { value: 'secondary' as const, label: 'Secondary', className: 'bg-white text-gray-900' },
  {
    value: 'outline' as const,
    label: 'Outline',
    className: 'border border-white text-white bg-transparent',
  },
] as const;

export function HeroCTAButton({ text, link, style, onChange }: HeroCTAButtonProps) {
  return (
    <div className="space-y-4">
      {/* Button Text */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-gray-700">Button Text</label>
        <input
          type="text"
          value={text}
          onChange={(e) => onChange({ ctaText: e.target.value })}
          placeholder="Shop Now"
          maxLength={40}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Button Link */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-gray-700">Button URL</label>
        <input
          type="text"
          value={link}
          onChange={(e) => onChange({ ctaLink: e.target.value })}
          placeholder="/products"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <p className="text-xs text-gray-400">Relative path (e.g. /products) or full URL</p>
      </div>

      {/* Button Style */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Button Style</label>
        <div className="flex flex-wrap gap-3">
          {STYLE_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange({ ctaStyle: opt.value })}
              className={`rounded-md border-2 px-4 py-2 text-sm transition-colors ${
                style === opt.value ? 'border-blue-600 ring-2 ring-blue-200' : 'border-transparent'
              }`}
            >
              <span
                className={`inline-block rounded-md px-4 py-1.5 text-sm font-medium ${opt.className}`}
              >
                {opt.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Preview */}
      {text && (
        <div className="space-y-1">
          <p className="text-xs font-medium text-gray-500">Preview</p>
          <div className="flex items-center gap-3 rounded-md bg-gray-800 p-4">
            <button
              type="button"
              className={`rounded-md px-6 py-2 text-sm font-medium ${
                style === 'primary'
                  ? 'bg-blue-600 text-white'
                  : style === 'secondary'
                    ? 'bg-white text-gray-900'
                    : 'border border-white text-white'
              }`}
            >
              {text}
            </button>
            {link && <span className="text-xs text-gray-400">→ {link}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
