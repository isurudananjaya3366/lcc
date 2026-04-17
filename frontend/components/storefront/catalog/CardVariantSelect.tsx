'use client';

import { cn } from '@/lib/utils';
import type { StoreProductVariant } from '@/types/store/product';

// ── Types ──────────────────────────────────────────────────────

export interface VariantOption {
  id: string;
  name: string;
  value: string;
  inStock: boolean;
  imageUrl?: string;
}

type DisplayType = 'dropdown' | 'swatches' | 'buttons';

interface CardVariantSelectProps {
  variants: StoreProductVariant[];
  selectedVariantId?: string | null;
  onVariantChange: (id: string) => void;
  displayType?: DisplayType;
  className?: string;
}

// ── Color swatch map ──────────────────────────────────────────

const COLOR_MAP: Record<string, string> = {
  red: '#EF4444',
  blue: '#3B82F6',
  green: '#22C55E',
  black: '#000000',
  white: '#FFFFFF',
  yellow: '#EAB308',
  purple: '#A855F7',
  pink: '#EC4899',
  orange: '#F97316',
  gray: '#6B7280',
  grey: '#6B7280',
  navy: '#1E3A8A',
  brown: '#92400E',
  beige: '#D2B48C',
  teal: '#14B8A6',
};

function resolveColor(value: string): string {
  return COLOR_MAP[value.toLowerCase()] ?? '#9CA3AF';
}

function isColorAttribute(attributeName: string): boolean {
  return ['color', 'colour', 'shade'].includes(attributeName.toLowerCase());
}

// ── Dropdown Display ──────────────────────────────────────────

function DropdownSelect({
  variants,
  selectedVariantId,
  onVariantChange,
}: Pick<CardVariantSelectProps, 'variants' | 'selectedVariantId' | 'onVariantChange'>) {
  return (
    <select
      value={selectedVariantId ?? ''}
      onChange={(e) => onVariantChange(e.target.value)}
      className="w-full text-sm border border-gray-300 rounded-md px-2 py-1.5 bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      aria-label="Select variant"
    >
      <option value="" disabled>
        Select option
      </option>
      {variants.map((v) => (
        <option key={v.id} value={v.id} disabled={!v.isAvailable}>
          {v.name}
          {!v.isAvailable ? ' (Out of Stock)' : ''}
        </option>
      ))}
    </select>
  );
}

// ── Swatch Display ────────────────────────────────────────────

function SwatchSelect({
  variants,
  selectedVariantId,
  onVariantChange,
}: Pick<CardVariantSelectProps, 'variants' | 'selectedVariantId' | 'onVariantChange'>) {
  return (
    <div className="flex flex-wrap gap-1.5" role="group" aria-label="Select color">
      {variants.map((v) => {
        const colorOption = v.options.find((o) => isColorAttribute(o.name));
        const colorValue = colorOption?.value ?? v.name;
        const bgColor = resolveColor(colorValue);
        const isSelected = v.id === selectedVariantId;
        const isLight = ['white', 'beige', 'yellow'].includes(colorValue.toLowerCase());

        return (
          <button
            key={v.id}
            type="button"
            title={v.name}
            disabled={!v.isAvailable}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              onVariantChange(v.id);
            }}
            className={cn(
              'relative w-7 h-7 rounded-full transition-all',
              isSelected && 'ring-2 ring-blue-500 ring-offset-2',
              !v.isAvailable && 'opacity-40 cursor-not-allowed',
              isLight && 'border border-gray-300'
            )}
            style={{ backgroundColor: bgColor }}
            aria-label={v.name}
            aria-pressed={isSelected}
          >
            {isSelected && (
              <svg
                className={cn(
                  'absolute inset-0 m-auto w-3.5 h-3.5',
                  isLight ? 'text-gray-700' : 'text-white'
                )}
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 0 1 0 1.414l-8 8a1 1 0 0 1-1.414 0l-4-4a1 1 0 1 1 1.414-1.414L8 12.586l7.293-7.293a1 1 0 0 1 1.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            {!v.isAvailable && (
              <span
                className="absolute inset-0 rounded-full"
                style={{
                  background:
                    'repeating-linear-gradient(45deg,transparent,transparent 4px,rgba(0,0,0,.15) 4px,rgba(0,0,0,.15) 5px)',
                }}
                aria-hidden="true"
              />
            )}
          </button>
        );
      })}
    </div>
  );
}

// ── Button Display ────────────────────────────────────────────

function ButtonSelect({
  variants,
  selectedVariantId,
  onVariantChange,
}: Pick<CardVariantSelectProps, 'variants' | 'selectedVariantId' | 'onVariantChange'>) {
  return (
    <div className="flex flex-wrap gap-1.5" role="group" aria-label="Select size / option">
      {variants.map((v) => {
        const isSelected = v.id === selectedVariantId;
        return (
          <button
            key={v.id}
            type="button"
            disabled={!v.isAvailable}
            onClick={(e) => {
              e.stopPropagation();
              e.preventDefault();
              onVariantChange(v.id);
            }}
            className={cn(
              'min-w-[40px] h-9 px-3 border rounded-md text-sm font-medium transition-colors',
              isSelected
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-900 border-gray-300 hover:border-blue-300',
              !v.isAvailable && 'opacity-40 cursor-not-allowed line-through'
            )}
            aria-pressed={isSelected}
            aria-label={v.name}
          >
            {v.options[0]?.value ?? v.name}
          </button>
        );
      })}
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────

export function CardVariantSelect({
  variants,
  selectedVariantId,
  onVariantChange,
  displayType = 'buttons',
  className,
}: CardVariantSelectProps) {
  if (!variants || variants.length === 0) return null;

  // Auto-detect display type from first variant options
  const effectiveType: DisplayType = (() => {
    if (displayType !== 'buttons') return displayType;
    const firstOption = variants[0]?.options[0];
    if (firstOption && isColorAttribute(firstOption.name)) return 'swatches';
    if (variants.length > 6) return 'dropdown';
    return 'buttons';
  })();

  return (
    <div className={cn('px-3 pb-2', className)}>
      {effectiveType === 'dropdown' && (
        <DropdownSelect
          variants={variants}
          selectedVariantId={selectedVariantId}
          onVariantChange={onVariantChange}
        />
      )}
      {effectiveType === 'swatches' && (
        <SwatchSelect
          variants={variants}
          selectedVariantId={selectedVariantId}
          onVariantChange={onVariantChange}
        />
      )}
      {effectiveType === 'buttons' && (
        <ButtonSelect
          variants={variants}
          selectedVariantId={selectedVariantId}
          onVariantChange={onVariantChange}
        />
      )}
    </div>
  );
}
