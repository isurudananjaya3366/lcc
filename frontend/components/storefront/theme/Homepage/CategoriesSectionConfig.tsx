'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface CategoriesSectionSettings {
  title: string;
  columns: 3 | 4 | 6;
  showImages: boolean;
  showProductCount: boolean;
  showDescription: boolean;
}

export interface CategoriesSectionConfigProps {
  config: CategoriesSectionSettings;
  onChange: (config: CategoriesSectionSettings) => void;
}

const DEFAULTS: CategoriesSectionSettings = {
  title: 'Shop by Category',
  columns: 4,
  showImages: true,
  showProductCount: true,
  showDescription: false,
};

export function CategoriesSectionConfig({
  config = DEFAULTS,
  onChange,
}: CategoriesSectionConfigProps) {
  const update = (partial: Partial<CategoriesSectionSettings>) => {
    onChange({ ...config, ...partial });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Categories Section</h3>

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="cat-title">Section Title</Label>
        <Input
          id="cat-title"
          value={config.title}
          onChange={(e) => update({ title: e.target.value.slice(0, 50) })}
          placeholder="Shop by Category"
          maxLength={50}
        />
        <p className="text-xs text-muted-foreground">{config.title.length}/50 characters</p>
      </div>

      {/* Columns */}
      <div className="space-y-2">
        <Label>Column Count</Label>
        <Select
          value={String(config.columns)}
          onValueChange={(v) => update({ columns: Number(v) as 3 | 4 | 6 })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="3">3 columns</SelectItem>
            <SelectItem value="4">4 columns</SelectItem>
            <SelectItem value="6">6 columns</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Display options */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium">Display Options</h4>
        <div className="flex items-center justify-between">
          <Label htmlFor="cat-images">Show Images</Label>
          <Switch
            id="cat-images"
            checked={config.showImages}
            onCheckedChange={(v) => update({ showImages: v })}
          />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="cat-count">Show Product Count</Label>
          <Switch
            id="cat-count"
            checked={config.showProductCount}
            onCheckedChange={(v) => update({ showProductCount: v })}
          />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="cat-desc">Show Description</Label>
          <Switch
            id="cat-desc"
            checked={config.showDescription}
            onCheckedChange={(v) => update({ showDescription: v })}
          />
        </div>
      </div>
    </div>
  );
}
