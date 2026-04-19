'use client';

import { useTheme } from '@/hooks/storefront/useTheme';

export function HeaderColorPreview() {
  const { colors } = useTheme();
  const primary = colors?.primary ?? '#2563eb';
  const bgColor = colors?.background ?? '#ffffff';

  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-gray-700">Header Preview</h4>
      <div
        className="rounded-lg overflow-hidden border border-gray-200"
        style={{ backgroundColor: bgColor }}
      >
        <div
          className="flex items-center justify-between px-4 py-3"
          style={{ backgroundColor: primary }}
        >
          <span className="text-sm font-bold text-white">StoreName</span>
          <nav className="flex gap-4">
            <span className="text-xs text-white/80 hover:text-white cursor-pointer">Home</span>
            <span className="text-xs text-white/80 hover:text-white cursor-pointer">Products</span>
            <span className="text-xs text-white/80 hover:text-white cursor-pointer">Contact</span>
          </nav>
        </div>
        <div className="px-4 py-3">
          <p className="text-xs text-gray-500">Page content area</p>
        </div>
      </div>
    </div>
  );
}
