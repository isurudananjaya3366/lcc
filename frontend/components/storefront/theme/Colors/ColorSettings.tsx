'use client';

import { Palette } from 'lucide-react';
import { useTheme } from '@/hooks/storefront/useTheme';
import { PrimaryColorPicker } from './PrimaryColorPicker';
import { SecondaryColorPicker } from './SecondaryColorPicker';
import { AccentColor } from './AccentColor';
import { BackgroundColor } from './BackgroundColor';
import { TextColor } from './TextColor';
import { ColorPresets } from './ColorPresets';
import { GeneratePalette } from './GeneratePalette';
import { ContrastCheck } from './ContrastCheck';
import { ApplyColors } from './ApplyColors';
import { ColorReset } from './ColorReset';
import { ButtonColorPreview } from './ButtonColorPreview';
import { LinkColorPreview } from './LinkColorPreview';
import { HeaderColorPreview } from './HeaderColorPreview';

export function ColorSettings() {
  const { colors } = useTheme();

  const primaryColor = colors?.primary ?? '#2563eb';
  const secondaryColor = colors?.secondary ?? '#64748b';
  const textColor = colors?.text.primary ?? '#0f172a';
  const bgColor = colors?.background ?? '#ffffff';

  return (
    <div className="space-y-6 p-6">
      {/* Heading */}
      <div className="flex items-center gap-2">
        <Palette className="h-6 w-6 text-blue-600" />
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Color Customization</h2>
          <p className="text-sm text-gray-600">
            Customize your storefront colors to match your brand identity.
          </p>
        </div>
      </div>

      {/* Color Presets */}
      <ColorPresets />

      {/* Brand Colors */}
      <section className="space-y-4 rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800">Brand Colors</h3>
        <div className="grid gap-6 sm:grid-cols-2">
          <PrimaryColorPicker />
          <SecondaryColorPicker />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <GeneratePalette baseColor={primaryColor} label="Primary Shades" />
          <GeneratePalette baseColor={secondaryColor} label="Secondary Shades" />
        </div>
      </section>

      {/* UI Colors */}
      <section className="space-y-4 rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800">UI Colors</h3>
        <AccentColor />
      </section>

      {/* Page Colors */}
      <section className="space-y-4 rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800">Page Colors</h3>
        <div className="grid gap-6 sm:grid-cols-2">
          <BackgroundColor />
          <TextColor />
        </div>
      </section>

      {/* Contrast Check */}
      <ContrastCheck
        foreground={textColor}
        background={bgColor}
        label="Text / Background Contrast"
      />

      {/* Previews */}
      <section className="space-y-4 rounded-lg border border-gray-200 p-4">
        <h3 className="text-lg font-semibold text-gray-800">Live Preview</h3>
        <ButtonColorPreview />
        <LinkColorPreview />
        <HeaderColorPreview />
      </section>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <ApplyColors />
        <ColorReset />
      </div>
    </div>
  );
}
