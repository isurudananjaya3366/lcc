'use client';

import { useState } from 'react';
import { Smartphone } from 'lucide-react';
import { LogoUpload } from './LogoUpload';
import { LogoPreview } from './LogoPreview';

export interface MobileLogoProps {
  mobileLogoUrl: string;
  onUpload: (url: string) => void;
}

export function MobileLogo({ mobileLogoUrl, onUpload }: MobileLogoProps) {
  const [enabled, setEnabled] = useState(!!mobileLogoUrl);

  const handleToggle = () => {
    const next = !enabled;
    setEnabled(next);
    if (!next) onUpload('');
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Smartphone className="h-5 w-5 text-gray-500" />
        <h3 className="text-lg font-semibold text-gray-800">Mobile Logo (Optional)</h3>
      </div>

      {/* Toggle */}
      <label className="flex cursor-pointer items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={enabled}
          onChange={handleToggle}
          className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
        />
        Use a different logo on mobile
      </label>

      <p className="text-xs text-gray-500">
        Mobile screens benefit from a simplified or icon-only version of your logo. Breakpoint: &lt;
        768px.
      </p>

      {enabled && (
        <div className="space-y-3 rounded-md border border-gray-200 p-3">
          <LogoUpload
            logoType="mobile"
            currentUrl={mobileLogoUrl}
            onUploadComplete={onUpload}
            maxSizeMB={0.5}
          />
          {mobileLogoUrl && (
            <>
              <LogoPreview
                imageUrl={mobileLogoUrl}
                logoHeight={40}
                alt="Mobile logo preview"
                containerHeight={100}
              />
              {/* Mobile mockup */}
              <div className="mx-auto w-56 rounded-xl border-2 border-gray-300 bg-white">
                <div className="flex items-center justify-between border-b border-gray-200 px-3 py-2">
                  <span className="text-lg text-gray-400">☰</span>
                  <img src={mobileLogoUrl} alt="Mobile logo" className="h-6 object-contain" />
                  <span className="text-lg text-gray-400">🛒</span>
                </div>
                <div className="flex h-24 items-center justify-center text-xs text-gray-300">
                  Page Content
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {!enabled && (
        <p className="text-xs italic text-gray-400">Main logo will be used on all screen sizes.</p>
      )}
    </div>
  );
}
