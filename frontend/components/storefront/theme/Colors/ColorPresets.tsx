'use client';

import { useState, useCallback } from 'react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { ColorSwatchPreview } from './ColorSwatchPreview';

interface ColorPreset {
  id: string;
  name: string;
  description: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    text: string;
  };
}

const PRESETS: ColorPreset[] = [
  {
    id: 'modern-blue',
    name: 'Modern Blue',
    description: 'Professional',
    colors: {
      primary: '#2563eb',
      secondary: '#64748b',
      accent: '#3b82f6',
      background: '#ffffff',
      text: '#0f172a',
    },
  },
  {
    id: 'forest-green',
    name: 'Forest Green',
    description: 'Natural',
    colors: {
      primary: '#059669',
      secondary: '#374151',
      accent: '#10b981',
      background: '#ffffff',
      text: '#111827',
    },
  },
  {
    id: 'royal-purple',
    name: 'Royal Purple',
    description: 'Elegant',
    colors: {
      primary: '#7c3aed',
      secondary: '#4b5563',
      accent: '#a855f7',
      background: '#ffffff',
      text: '#111827',
    },
  },
  {
    id: 'coral',
    name: 'Coral',
    description: 'Energetic',
    colors: {
      primary: '#f97316',
      secondary: '#475569',
      accent: '#fb923c',
      background: '#ffffff',
      text: '#0f172a',
    },
  },
  {
    id: 'midnight',
    name: 'Midnight',
    description: 'Modern',
    colors: {
      primary: '#1e293b',
      secondary: '#64748b',
      accent: '#38bdf8',
      background: '#ffffff',
      text: '#0f172a',
    },
  },
  {
    id: 'sunset',
    name: 'Sunset',
    description: 'Warm',
    colors: {
      primary: '#dc2626',
      secondary: '#f59e0b',
      accent: '#fbbf24',
      background: '#ffffff',
      text: '#111827',
    },
  },
];

export function ColorPresets() {
  const { colors, updateTheme } = useTheme();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const handleSelect = useCallback(
    (preset: ColorPreset) => {
      setSelectedId(preset.id);
      void updateTheme({
        colors: {
          primary: preset.colors.primary,
          secondary: preset.colors.secondary,
          accent: preset.colors.accent,
          background: preset.colors.background,
          text: { primary: preset.colors.text },
        },
      });
    },
    [updateTheme]
  );

  return (
    <div className="space-y-3">
      <div>
        <h4 className="text-sm font-semibold text-gray-700">Color Presets</h4>
        <p className="text-xs text-gray-500">Choose a curated color scheme</p>
      </div>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
        {PRESETS.map((preset) => (
          <button
            key={preset.id}
            type="button"
            onClick={() => handleSelect(preset)}
            className={`flex flex-col items-center gap-2 rounded-lg border-2 p-3 transition-all hover:scale-[1.02] ${
              selectedId === preset.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <span className="text-xs font-medium">{preset.name}</span>
            <div className="flex gap-1.5">
              <ColorSwatchPreview color={preset.colors.primary} size="sm" />
              <ColorSwatchPreview color={preset.colors.secondary} size="sm" />
              <ColorSwatchPreview color={preset.colors.accent} size="sm" />
            </div>
            <span className="text-[10px] text-gray-400">{preset.description}</span>
            {selectedId === preset.id && <span className="text-xs text-blue-600">✓</span>}
          </button>
        ))}
      </div>
    </div>
  );
}
