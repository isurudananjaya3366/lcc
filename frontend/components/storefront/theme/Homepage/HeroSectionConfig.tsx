'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';

export interface HeroSectionSettings {
  title: string;
  subtitle: string;
  ctaText: string;
  ctaLink: string;
  backgroundImage: string;
  overlayOpacity: number;
}

export interface HeroSectionConfigProps {
  config: HeroSectionSettings;
  onChange: (config: HeroSectionSettings) => void;
}

const DEFAULTS: HeroSectionSettings = {
  title: '',
  subtitle: '',
  ctaText: '',
  ctaLink: '',
  backgroundImage: '',
  overlayOpacity: 40,
};

export function HeroSectionConfig({ config = DEFAULTS, onChange }: HeroSectionConfigProps) {
  const update = (partial: Partial<HeroSectionSettings>) => {
    onChange({ ...config, ...partial });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Hero Section</h3>

      {/* Background Image */}
      <div className="space-y-2">
        <Label htmlFor="hero-bg">Background Image URL</Label>
        <Input
          id="hero-bg"
          value={config.backgroundImage}
          onChange={(e) => update({ backgroundImage: e.target.value })}
          placeholder="https://example.com/hero.jpg"
        />
        <p className="text-xs text-muted-foreground">
          Recommended: 1920×800px, JPEG/PNG/WebP, max 2MB
        </p>
      </div>

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="hero-title">Heading</Label>
        <Input
          id="hero-title"
          value={config.title}
          onChange={(e) => update({ title: e.target.value.slice(0, 60) })}
          placeholder="Welcome to our store"
          maxLength={60}
        />
        <p className="text-xs text-muted-foreground">{config.title.length}/60 characters</p>
      </div>

      {/* Subtitle */}
      <div className="space-y-2">
        <Label htmlFor="hero-subtitle">Subtitle</Label>
        <Textarea
          id="hero-subtitle"
          value={config.subtitle}
          onChange={(e) => update({ subtitle: e.target.value.slice(0, 150) })}
          placeholder="Discover our latest collection"
          maxLength={150}
          rows={2}
        />
        <p className="text-xs text-muted-foreground">{config.subtitle.length}/150 characters</p>
      </div>

      {/* CTA */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium">Call to Action</h4>
        <div className="space-y-2">
          <Label htmlFor="hero-cta-text">Button Text</Label>
          <Input
            id="hero-cta-text"
            value={config.ctaText}
            onChange={(e) => update({ ctaText: e.target.value.slice(0, 30) })}
            placeholder="Shop Now"
            maxLength={30}
          />
          <p className="text-xs text-muted-foreground">{config.ctaText.length}/30 characters</p>
        </div>
        <div className="space-y-2">
          <Label htmlFor="hero-cta-link">Button URL</Label>
          <Input
            id="hero-cta-link"
            value={config.ctaLink}
            onChange={(e) => update({ ctaLink: e.target.value })}
            placeholder="/products"
          />
        </div>
      </div>

      {/* Overlay */}
      <div className="space-y-2">
        <Label>Overlay Opacity: {config.overlayOpacity}%</Label>
        <Slider
          value={[config.overlayOpacity]}
          onValueChange={([v]) => update({ overlayOpacity: v })}
          min={0}
          max={100}
          step={5}
        />
      </div>
    </div>
  );
}
