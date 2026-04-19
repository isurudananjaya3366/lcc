'use client';

import React from 'react';
import { HeroSectionConfig } from './HeroSectionConfig';
import { FeaturedProductsConfig } from './FeaturedProductsConfig';
import { CategoriesSectionConfig } from './CategoriesSectionConfig';
import { TestimonialsConfig } from './TestimonialsConfig';
import { NewsletterConfig } from './NewsletterConfig';

import type { HomepageSection } from './types';

export interface SectionSettingsProps {
  section: HomepageSection;
  onChange: (settings: Record<string, unknown>) => void;
}

export function SectionSettings({ section, onChange }: SectionSettingsProps) {
  const settings = section.settings as Record<string, unknown>;

  switch (section.type) {
    case 'hero':
      return (
        <HeroSectionConfig
          config={settings as any}
          onChange={(c) => onChange(c as unknown as Record<string, unknown>)}
        />
      );
    case 'featured':
      return (
        <FeaturedProductsConfig
          config={settings as any}
          onChange={(c) => onChange(c as unknown as Record<string, unknown>)}
        />
      );
    case 'categories':
      return (
        <CategoriesSectionConfig
          config={settings as any}
          onChange={(c) => onChange(c as unknown as Record<string, unknown>)}
        />
      );
    case 'testimonials':
      return (
        <TestimonialsConfig
          config={settings as any}
          onChange={(c) => onChange(c as unknown as Record<string, unknown>)}
        />
      );
    case 'newsletter':
      return (
        <NewsletterConfig
          config={settings as any}
          onChange={(c) => onChange(c as unknown as Record<string, unknown>)}
        />
      );
    default:
      return (
        <div className="p-4 text-sm text-muted-foreground">
          No settings available for this section type.
        </div>
      );
  }
}
