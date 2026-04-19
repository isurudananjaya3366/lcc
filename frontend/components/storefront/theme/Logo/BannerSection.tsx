'use client';

import { useState } from 'react';
import { LayoutTemplate, ChevronDown, ChevronUp } from 'lucide-react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { HeroImageUpload } from './HeroImageUpload';
import { HeroTextOverlay } from './HeroTextOverlay';
import { HeroCTAButton } from './HeroCTAButton';

export interface BannerConfig {
  heroImageUrl: string;
  heroTitle: string;
  heroSubtitle: string;
  textPosition: 'left' | 'center' | 'right';
  textColor: string;
  overlayEnabled: boolean;
  overlayOpacity: number;
  ctaText: string;
  ctaLink: string;
  ctaStyle: 'primary' | 'secondary' | 'outline';
}

const DEFAULT_BANNER: BannerConfig = {
  heroImageUrl: '',
  heroTitle: '',
  heroSubtitle: '',
  textPosition: 'center',
  textColor: '#FFFFFF',
  overlayEnabled: true,
  overlayOpacity: 0.4,
  ctaText: '',
  ctaLink: '',
  ctaStyle: 'primary',
};

export function BannerSection() {
  const { homepage, updateTheme } = useTheme();

  const [config, setConfig] = useState<BannerConfig>({
    ...DEFAULT_BANNER,
    heroImageUrl: homepage?.hero.backgroundImage ?? '',
    heroTitle: homepage?.hero.title ?? '',
    heroSubtitle: homepage?.hero.subtitle ?? '',
    ctaText: homepage?.hero.ctaText ?? '',
    ctaLink: homepage?.hero.ctaLink ?? '',
  });
  const [expanded, setExpanded] = useState(true);

  const update = <K extends keyof BannerConfig>(key: K, value: BannerConfig[K]) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    await updateTheme({
      homepage: {
        hero: {
          title: config.heroTitle,
          subtitle: config.heroSubtitle,
          ctaText: config.ctaText,
          ctaLink: config.ctaLink,
          backgroundImage: config.heroImageUrl,
          backgroundOverlay: config.overlayEnabled
            ? `rgba(0,0,0,${config.overlayOpacity})`
            : undefined,
        },
      },
    });
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <button
        type="button"
        className="flex w-full items-center gap-2"
        onClick={() => setExpanded(!expanded)}
      >
        <LayoutTemplate className="h-6 w-6 text-blue-600" />
        <div className="text-left">
          <h2 className="text-2xl font-bold text-gray-900">Banner &amp; Hero Section</h2>
          <p className="text-sm text-gray-600">
            Configure homepage hero image and promotional banners
          </p>
        </div>
        {expanded ? (
          <ChevronUp className="ml-auto h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDown className="ml-auto h-5 w-5 text-gray-400" />
        )}
      </button>

      {expanded && (
        <div className="space-y-6">
          {/* Hero Image */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Hero Image</h3>
            <HeroImageUpload
              currentImage={config.heroImageUrl}
              onUploadComplete={(url) => update('heroImageUrl', url)}
            />
          </section>

          {/* Text Overlay */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Text Overlay</h3>
            <HeroTextOverlay
              heroImage={config.heroImageUrl}
              title={config.heroTitle}
              subtitle={config.heroSubtitle}
              position={config.textPosition}
              textColor={config.textColor}
              overlayEnabled={config.overlayEnabled}
              overlayOpacity={config.overlayOpacity}
              onChange={(updates) => setConfig((prev) => ({ ...prev, ...updates }))}
            />
          </section>

          {/* CTA Button */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Call-to-Action Button</h3>
            <HeroCTAButton
              text={config.ctaText}
              link={config.ctaLink}
              style={config.ctaStyle}
              onChange={(updates) => setConfig((prev) => ({ ...prev, ...updates }))}
            />
          </section>

          {/* Live preview */}
          {config.heroImageUrl && (
            <section className="space-y-2">
              <h3 className="text-sm font-semibold text-gray-800">Live Preview</h3>
              <div
                className="relative flex min-h-[200px] items-center justify-center overflow-hidden rounded-lg bg-gray-200 bg-cover bg-center"
                style={{ backgroundImage: `url(${config.heroImageUrl})` }}
              >
                {config.overlayEnabled && (
                  <div
                    className="absolute inset-0"
                    style={{ backgroundColor: `rgba(0,0,0,${config.overlayOpacity})` }}
                  />
                )}
                <div
                  className={`relative z-10 w-full px-8 py-10 ${
                    config.textPosition === 'left'
                      ? 'text-left'
                      : config.textPosition === 'right'
                        ? 'text-right'
                        : 'text-center'
                  }`}
                >
                  {config.heroTitle && (
                    <h2 className="text-3xl font-bold" style={{ color: config.textColor }}>
                      {config.heroTitle}
                    </h2>
                  )}
                  {config.heroSubtitle && (
                    <p className="mt-2 text-lg" style={{ color: config.textColor }}>
                      {config.heroSubtitle}
                    </p>
                  )}
                  {config.ctaText && (
                    <button
                      type="button"
                      className={`mt-4 rounded-md px-6 py-2 text-sm font-medium ${
                        config.ctaStyle === 'primary'
                          ? 'bg-blue-600 text-white'
                          : config.ctaStyle === 'secondary'
                            ? 'bg-white text-gray-900'
                            : 'border border-white text-white'
                      }`}
                    >
                      {config.ctaText}
                    </button>
                  )}
                </div>
              </div>
            </section>
          )}

          {/* Save */}
          <button
            type="button"
            onClick={handleSave}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Save Banner Settings
          </button>
        </div>
      )}
    </div>
  );
}
