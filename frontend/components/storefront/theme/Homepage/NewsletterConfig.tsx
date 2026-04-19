'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export interface NewsletterSettings {
  title: string;
  subtitle: string;
  buttonText: string;
  placeholder: string;
}

export interface NewsletterConfigProps {
  config: NewsletterSettings;
  onChange: (config: NewsletterSettings) => void;
}

const DEFAULTS: NewsletterSettings = {
  title: 'Stay Updated',
  subtitle: 'Subscribe to our newsletter for the latest deals and updates.',
  buttonText: 'Subscribe',
  placeholder: 'Enter your email',
};

export function NewsletterConfig({ config = DEFAULTS, onChange }: NewsletterConfigProps) {
  const update = (partial: Partial<NewsletterSettings>) => {
    onChange({ ...config, ...partial });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Newsletter Signup</h3>

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="news-title">Title</Label>
        <Input
          id="news-title"
          value={config.title}
          onChange={(e) => update({ title: e.target.value.slice(0, 50) })}
          placeholder="Stay Updated"
          maxLength={50}
        />
        <p className="text-xs text-muted-foreground">{config.title.length}/50 characters</p>
      </div>

      {/* Subtitle */}
      <div className="space-y-2">
        <Label htmlFor="news-subtitle">Subtitle</Label>
        <Input
          id="news-subtitle"
          value={config.subtitle}
          onChange={(e) => update({ subtitle: e.target.value.slice(0, 100) })}
          placeholder="Subscribe for the latest updates"
          maxLength={100}
        />
        <p className="text-xs text-muted-foreground">{config.subtitle.length}/100 characters</p>
      </div>

      {/* Button Text */}
      <div className="space-y-2">
        <Label htmlFor="news-btn">Button Text</Label>
        <Input
          id="news-btn"
          value={config.buttonText}
          onChange={(e) => update({ buttonText: e.target.value.slice(0, 20) })}
          placeholder="Subscribe"
          maxLength={20}
        />
        <p className="text-xs text-muted-foreground">{config.buttonText.length}/20 characters</p>
      </div>

      {/* Placeholder */}
      <div className="space-y-2">
        <Label htmlFor="news-placeholder">Input Placeholder</Label>
        <Input
          id="news-placeholder"
          value={config.placeholder}
          onChange={(e) => update({ placeholder: e.target.value.slice(0, 40) })}
          placeholder="Enter your email"
          maxLength={40}
        />
      </div>

      {/* Live preview */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium">Preview</h4>
        <div className="border rounded-lg p-4 bg-muted/30 text-center space-y-2">
          <p className="font-semibold">{config.title || 'Title'}</p>
          <p className="text-sm text-muted-foreground">{config.subtitle || 'Subtitle'}</p>
          <div className="flex max-w-sm mx-auto gap-2">
            <div className="flex-1 h-9 rounded-md border bg-background px-3 flex items-center text-sm text-muted-foreground">
              {config.placeholder || 'Email'}
            </div>
            <div className="h-9 px-4 rounded-md bg-primary text-primary-foreground flex items-center text-sm font-medium">
              {config.buttonText || 'Subscribe'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
