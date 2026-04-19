'use client';

// ================================================================
// Body Font Selector
// ================================================================
// Dropdown for choosing the body text font family.
// ================================================================

import { useCallback, useState } from 'react';
import { ChevronDown, Check } from 'lucide-react';
import { fontList, type FontDefinition, type FontCategory } from './FontList';
import { FontLoadingState } from './FontLoadingState';
import { useFontLoader } from './FontLoader';

interface BodyFontSelectorProps {
  value: string;
  onChange: (fontName: string, fontFamily: string) => void;
  className?: string;
}

const BODY_CATEGORIES: FontCategory[] = ['sans-serif', 'serif'];

export function BodyFontSelector({ value, onChange, className }: BodyFontSelectorProps) {
  const [open, setOpen] = useState(false);
  const { status, load } = useFontLoader();

  const bodyFonts = fontList.filter((f) => BODY_CATEGORIES.includes(f.category) && f.recommended);

  const handleSelect = useCallback(
    async (font: FontDefinition) => {
      setOpen(false);
      await load(font);
      onChange(font.name, font.family);
    },
    [onChange, load]
  );

  return (
    <div className={`space-y-1.5 ${className ?? ''}`}>
      <label className="block text-sm font-medium text-gray-700">Body Font</label>
      <p className="text-xs text-gray-500">Choose a readable font for body content</p>

      <div className="relative">
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="flex w-full items-center justify-between rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm hover:border-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          aria-haspopup="listbox"
          aria-expanded={open}
        >
          <span>{value || 'Select font'}</span>
          <ChevronDown className="h-4 w-4 text-gray-400" />
        </button>

        {open && (
          <ul
            role="listbox"
            className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-gray-200 bg-white py-1 shadow-lg"
          >
            {bodyFonts.map((font) => {
              const selected = font.name === value;
              return (
                <li
                  key={font.id}
                  role="option"
                  aria-selected={selected}
                  onClick={() => void handleSelect(font)}
                  className={`flex cursor-pointer items-center justify-between px-3 py-2 text-sm hover:bg-gray-100 ${selected ? 'bg-blue-50' : ''}`}
                  style={{ fontFamily: font.family }}
                >
                  <span>{font.name}</span>
                  {selected && <Check className="h-4 w-4 text-blue-600" />}
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <FontLoadingState status={status} fontName={value} />
    </div>
  );
}
