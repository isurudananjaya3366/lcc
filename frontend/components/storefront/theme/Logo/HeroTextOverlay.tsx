'use client';

export interface HeroTextOverlayValues {
  title?: string;
  subtitle?: string;
  textPosition?: 'left' | 'center' | 'right';
  textColor?: string;
  overlayEnabled?: boolean;
  overlayOpacity?: number;
}

export interface HeroTextOverlayProps {
  heroImage: string;
  title?: string;
  subtitle?: string;
  position?: 'left' | 'center' | 'right';
  textColor?: string;
  overlayEnabled?: boolean;
  overlayOpacity?: number;
  onChange: (
    updates: Partial<{
      heroTitle: string;
      heroSubtitle: string;
      textPosition: 'left' | 'center' | 'right';
      textColor: string;
      overlayEnabled: boolean;
      overlayOpacity: number;
    }>
  ) => void;
}

const POSITION_OPTIONS = [
  { value: 'left' as const, label: 'Left' },
  { value: 'center' as const, label: 'Center' },
  { value: 'right' as const, label: 'Right' },
];

export function HeroTextOverlay({
  title = '',
  subtitle = '',
  position = 'center',
  textColor = '#FFFFFF',
  overlayEnabled = true,
  overlayOpacity = 0.4,
  onChange,
}: HeroTextOverlayProps) {
  return (
    <div className="space-y-4">
      {/* Title */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-gray-700">Hero Title</label>
        <input
          type="text"
          value={title}
          onChange={(e) => onChange({ heroTitle: e.target.value.slice(0, 60) })}
          placeholder="Welcome to Our Store"
          maxLength={60}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <span className="text-xs text-gray-400">{title.length} / 60 characters</span>
      </div>

      {/* Subtitle */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-gray-700">Hero Subtitle</label>
        <textarea
          value={subtitle}
          onChange={(e) => onChange({ heroSubtitle: e.target.value.slice(0, 150) })}
          placeholder="Discover amazing products at great prices"
          maxLength={150}
          rows={2}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
        <span className="text-xs text-gray-400">{subtitle.length} / 150 characters</span>
      </div>

      {/* Text Position */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-gray-700">Text Position</label>
        <div className="flex gap-2">
          {POSITION_OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange({ textPosition: opt.value })}
              className={`rounded-md border px-4 py-1.5 text-sm font-medium transition-colors ${
                position === opt.value
                  ? 'border-blue-600 bg-blue-50 text-blue-700'
                  : 'border-gray-300 text-gray-600 hover:bg-gray-50'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Text Color */}
      <div className="space-y-1">
        <label className="text-sm font-medium text-gray-700">Text Color</label>
        <div className="flex items-center gap-2">
          <input
            type="color"
            value={textColor}
            onChange={(e) => onChange({ textColor: e.target.value })}
            className="h-8 w-8 cursor-pointer rounded border border-gray-300"
          />
          <input
            type="text"
            value={textColor}
            onChange={(e) => onChange({ textColor: e.target.value })}
            className="w-24 rounded-md border border-gray-300 px-2 py-1 text-sm font-mono"
            maxLength={7}
          />
        </div>
      </div>

      {/* Background Overlay */}
      <div className="space-y-2">
        <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
          <input
            type="checkbox"
            checked={overlayEnabled}
            onChange={(e) => onChange({ overlayEnabled: e.target.checked })}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          Enable dark overlay
        </label>
        {overlayEnabled && (
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-400">0%</span>
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={overlayOpacity}
              onChange={(e) => onChange({ overlayOpacity: parseFloat(e.target.value) })}
              className="flex-1 accent-blue-600"
            />
            <span className="text-xs text-gray-400">100%</span>
            <span className="w-12 text-right text-sm font-medium text-gray-700">
              {Math.round(overlayOpacity * 100)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
