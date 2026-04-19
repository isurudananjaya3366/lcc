'use client';

import { CheckCircle2 } from 'lucide-react';
import { useTheme } from '@/hooks/storefront/useTheme';

export interface LogoApplyProps {
  logoUrl: string;
  logoAlt?: string;
  logoHeight?: number;
  logoWidth?: number;
  onApplied?: () => void;
}

export function LogoApply({
  logoUrl,
  logoAlt = 'Store Logo',
  logoHeight = 60,
  logoWidth = 200,
  onApplied,
}: LogoApplyProps) {
  const { updateTheme, logo } = useTheme();

  const isCurrentLogo = logo?.url === logoUrl;

  const handleApply = async () => {
    await updateTheme({
      logo: {
        url: logoUrl,
        alt: logoAlt,
        width: logoWidth,
        height: logoHeight,
      },
    });
    onApplied?.();
  };

  if (!logoUrl) {
    return (
      <div className="rounded-md border border-gray-200 bg-gray-50 px-4 py-3 text-sm text-gray-500">
        Upload a logo first to apply it to the store header.
      </div>
    );
  }

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 p-4">
      <h4 className="text-sm font-semibold text-gray-800">Apply Logo to Header</h4>

      {/* Header preview */}
      <div className="overflow-hidden rounded-md border border-gray-200 bg-white">
        <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
          <img src={logoUrl} alt={logoAlt} style={{ height: logoHeight, objectFit: 'contain' }} />
          <div className="flex gap-4 text-sm text-gray-400">
            <span>Products</span>
            <span>About</span>
            <span>Contact</span>
          </div>
        </div>
        <div className="flex h-16 items-center justify-center text-xs text-gray-300">
          Store Content
        </div>
      </div>

      {/* Apply button */}
      {isCurrentLogo ? (
        <div className="flex items-center gap-2 text-sm text-green-700">
          <CheckCircle2 className="h-4 w-4" />
          This logo is currently applied to the header.
        </div>
      ) : (
        <button
          type="button"
          onClick={handleApply}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Apply to Header
        </button>
      )}
    </div>
  );
}
