'use client';

// ================================================================
// Reset Typography – Reset to defaults
// ================================================================

import { useCallback } from 'react';
import { RotateCcw } from 'lucide-react';
import { defaultFonts } from '@/styles/theme/defaults';
import { applyTypography } from './ApplyFonts';

interface ResetTypographyProps {
  onReset?: () => void;
  className?: string;
}

export function ResetTypography({ onReset, className }: ResetTypographyProps) {
  const handleReset = useCallback(() => {
    applyTypography({
      headingFont: 'Inter',
      bodyFont: 'Open Sans',
      fontSize: 16,
      lineHeight: 1.5,
      headingWeight: defaultFonts.weights.bold,
      bodyWeight: defaultFonts.weights.normal,
    });
    onReset?.();
  }, [onReset]);

  return (
    <button
      type="button"
      onClick={handleReset}
      className={`inline-flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors ${className ?? ''}`}
    >
      <RotateCcw className="h-4 w-4" />
      Reset Typography
    </button>
  );
}
