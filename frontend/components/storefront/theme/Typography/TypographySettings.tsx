'use client';

// ================================================================
// Typography Settings – Main typography settings section UI
// ================================================================

import { useState, useCallback } from 'react';
import { Type } from 'lucide-react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { defaultFonts } from '@/styles/theme/defaults';
import { HeadingFontSelector } from './HeadingFontSelector';
import { BodyFontSelector } from './BodyFontSelector';
import { FontSizeScale } from './FontSizeScale';
import { LineHeightSetting } from './LineHeightSetting';
import { FontWeightOptions } from './FontWeightOptions';
import { FontPreview } from './FontPreview';
import { ApplyFonts, type TypographyConfig } from './ApplyFonts';
import { ResetTypography } from './ResetTypography';
import { TypographyPreview } from './TypographyPreview';

interface TypographySettingsProps {
  isCollapsed?: boolean;
  onUpdate?: (config: TypographyConfig) => void;
  className?: string;
}

export function TypographySettings({
  isCollapsed: initialCollapsed = false,
  onUpdate,
  className,
}: TypographySettingsProps) {
  const { fonts } = useTheme();

  const [headingFont, setHeadingFont] = useState(
    fonts?.heading ?? (defaultFonts.heading.split(',')[0] ?? '').replace(/'/g, '').trim()
  );
  const [headingFamily, setHeadingFamily] = useState(fonts?.heading ?? defaultFonts.heading);
  const [bodyFont, setBodyFont] = useState(
    fonts?.body ?? (defaultFonts.body.split(',')[0] ?? '').replace(/'/g, '').trim()
  );
  const [bodyFamily, setBodyFamily] = useState(fonts?.body ?? defaultFonts.body);
  const [fontSize, setFontSize] = useState(16);
  const [lineHeight, setLineHeight] = useState(1.5);
  const [headingWeight, setHeadingWeight] = useState(fonts?.weights?.bold ?? 700);
  const [bodyWeight, setBodyWeight] = useState(fonts?.weights?.normal ?? 400);
  const [collapsed, setCollapsed] = useState(initialCollapsed);

  const config: TypographyConfig = {
    headingFont,
    bodyFont,
    fontSize,
    lineHeight,
    headingWeight,
    bodyWeight,
  };

  const handleHeadingChange = useCallback(
    (name: string, family: string) => {
      setHeadingFont(name);
      setHeadingFamily(family);
      onUpdate?.({ ...config, headingFont: name });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [onUpdate, config]
  );

  const handleBodyChange = useCallback(
    (name: string, family: string) => {
      setBodyFont(name);
      setBodyFamily(family);
      onUpdate?.({ ...config, bodyFont: name });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [onUpdate, config]
  );

  const handleReset = useCallback(() => {
    setHeadingFont('Inter');
    setHeadingFamily("'Inter', sans-serif");
    setBodyFont('Open Sans');
    setBodyFamily("'Open Sans', sans-serif");
    setFontSize(16);
    setLineHeight(1.5);
    setHeadingWeight(700);
    setBodyWeight(400);
  }, []);

  return (
    <div className={`space-y-6 p-6 ${className ?? ''}`}>
      {/* Header */}
      <button
        type="button"
        onClick={() => setCollapsed(!collapsed)}
        className="flex w-full items-center gap-2 text-left"
      >
        <Type className="h-6 w-6 text-blue-600" />
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Typography &amp; Fonts</h2>
          <p className="text-sm text-gray-600">Customize fonts, sizes, and spacing</p>
        </div>
      </button>

      {collapsed ? null : (
        <>
          {/* Font Selection */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Font Selection</h3>
            <div className="grid gap-6 sm:grid-cols-2">
              <HeadingFontSelector value={headingFont} onChange={handleHeadingChange} />
              <BodyFontSelector value={bodyFont} onChange={handleBodyChange} />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <FontPreview fontFamily={headingFamily} fontType="heading" />
              <FontPreview fontFamily={bodyFamily} fontType="body" />
            </div>
          </section>

          {/* Font Scale */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Font Scale</h3>
            <div className="grid gap-6 sm:grid-cols-2">
              <FontSizeScale value={fontSize} onChange={setFontSize} />
              <LineHeightSetting value={lineHeight} onChange={setLineHeight} />
            </div>
          </section>

          {/* Font Styling */}
          <section className="space-y-4 rounded-lg border border-gray-200 p-4">
            <h3 className="text-lg font-semibold text-gray-800">Font Styling</h3>
            <FontWeightOptions
              headingWeight={headingWeight}
              bodyWeight={bodyWeight}
              onHeadingWeightChange={setHeadingWeight}
              onBodyWeightChange={setBodyWeight}
            />
          </section>

          {/* Full Preview */}
          <TypographyPreview
            headingFont={headingFamily}
            bodyFont={bodyFamily}
            headingWeight={headingWeight}
            bodyWeight={bodyWeight}
            fontSize={fontSize}
            lineHeight={lineHeight}
          />

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <ResetTypography onReset={handleReset} />
            <ApplyFonts config={config} />
          </div>
        </>
      )}
    </div>
  );
}
