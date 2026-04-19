'use client';

import { useState } from 'react';
import { ImageIcon, ChevronDown, ChevronUp, RotateCcw } from 'lucide-react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { LogoUpload } from './LogoUpload';
import { LogoPreview } from './LogoPreview';
import { LogoSizeControl } from './LogoSizeControl';
import { LogoAltText } from './LogoAltText';
import { FaviconUpload } from './FaviconUpload';
import { MobileLogo } from './MobileLogo';

export interface LogoSettingsData {
  logoUrl: string;
  faviconUrl: string;
  mobileLogoUrl: string;
  logoAlt: string;
  logoWidth: number;
  logoHeight: number;
}

const DEFAULT_SETTINGS: LogoSettingsData = {
  logoUrl: '',
  faviconUrl: '',
  mobileLogoUrl: '',
  logoAlt: 'Store Logo',
  logoWidth: 200,
  logoHeight: 60,
};

export function LogoSettings() {
  const { logo, updateTheme } = useTheme();

  const [settings, setSettings] = useState<LogoSettingsData>({
    logoUrl: logo?.url ?? DEFAULT_SETTINGS.logoUrl,
    faviconUrl: DEFAULT_SETTINGS.faviconUrl,
    mobileLogoUrl: DEFAULT_SETTINGS.mobileLogoUrl,
    logoAlt: logo?.alt ?? DEFAULT_SETTINGS.logoAlt,
    logoWidth: logo?.width ?? DEFAULT_SETTINGS.logoWidth,
    logoHeight: logo?.height ?? DEFAULT_SETTINGS.logoHeight,
  });

  const [expanded, setExpanded] = useState(true);

  const hasLogo = !!settings.logoUrl;
  const hasFavicon = !!settings.faviconUrl;

  const updateField = <K extends keyof LogoSettingsData>(key: K, value: LogoSettingsData[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleReset = () => {
    setSettings(DEFAULT_SETTINGS);
  };

  const handleSave = async () => {
    await updateTheme({
      logo: {
        url: settings.logoUrl,
        alt: settings.logoAlt,
        width: settings.logoWidth,
        height: settings.logoHeight,
      },
    });
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          type="button"
          className="flex flex-1 items-center gap-2"
          onClick={() => setExpanded(!expanded)}
        >
          <ImageIcon className="h-6 w-6 text-blue-600" />
          <div className="text-left">
            <h2 className="text-2xl font-bold text-gray-900">Logo Settings</h2>
            <p className="text-sm text-gray-600">
              Manage your store&apos;s logo, favicon, and mobile branding
            </p>
          </div>
          {hasLogo && (
            <span className="ml-2 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
              Configured
            </span>
          )}
          {expanded ? (
            <ChevronUp className="ml-auto h-5 w-5 text-gray-400" />
          ) : (
            <ChevronDown className="ml-auto h-5 w-5 text-gray-400" />
          )}
        </button>
      </div>

      {expanded && (
        <div className="space-y-6">
          {/* Main Logo */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Main Logo</h3>
            <LogoUpload
              logoType="main"
              currentUrl={settings.logoUrl}
              onUploadComplete={(url) => updateField('logoUrl', url)}
              maxSizeMB={2}
            />
            {settings.logoUrl && (
              <>
                <LogoPreview
                  imageUrl={settings.logoUrl}
                  logoHeight={settings.logoHeight}
                  alt={settings.logoAlt}
                  showDimensions
                />
                <LogoSizeControl
                  value={settings.logoHeight}
                  onChange={(h) => updateField('logoHeight', h)}
                />
                <LogoAltText
                  value={settings.logoAlt}
                  onChange={(alt) => updateField('logoAlt', alt)}
                />
              </>
            )}
          </section>

          {/* Favicon */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-800">Favicon</h3>
              {hasFavicon && (
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                  Set
                </span>
              )}
            </div>
            <FaviconUpload
              currentFavicon={settings.faviconUrl}
              onUploadComplete={(url) => updateField('faviconUrl', url)}
            />
          </section>

          {/* Mobile Logo */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <MobileLogo
              mobileLogoUrl={settings.mobileLogoUrl}
              onUpload={(url) => updateField('mobileLogoUrl', url)}
            />
          </section>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleSave}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Save Logo Settings
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center gap-1 rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              <RotateCcw className="h-4 w-4" />
              Reset to Defaults
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
