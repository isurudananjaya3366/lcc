'use client';

import { useCallback } from 'react';
import { RotateCcw } from 'lucide-react';
import { useTheme } from '@/hooks/storefront/useTheme';

interface ColorResetProps {
  className?: string;
}

export function ColorReset({ className }: ColorResetProps) {
  const { resetTheme } = useTheme();

  const handleReset = useCallback(() => {
    void resetTheme();
  }, [resetTheme]);

  return (
    <button
      type="button"
      onClick={handleReset}
      className={`inline-flex items-center gap-2 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors ${className ?? ''}`}
    >
      <RotateCcw className="h-4 w-4" />
      Reset to Default
    </button>
  );
}
