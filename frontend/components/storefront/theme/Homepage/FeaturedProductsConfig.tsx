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

export interface FeaturedProductsSettings {
  title: string;
  productCount: 4 | 6 | 8;
  layout: 'grid' | 'carousel';
  showPrice: boolean;
  showAddToCart: boolean;
  showRating: boolean;
}

export interface FeaturedProductsConfigProps {
  config: FeaturedProductsSettings;
  onChange: (config: FeaturedProductsSettings) => void;
}

const DEFAULTS: FeaturedProductsSettings = {
  title: 'Featured Products',
  productCount: 8,
  layout: 'grid',
  showPrice: true,
  showAddToCart: true,
  showRating: true,
};

export function FeaturedProductsConfig({
  config = DEFAULTS,
  onChange,
}: FeaturedProductsConfigProps) {
  const update = (partial: Partial<FeaturedProductsSettings>) => {
    onChange({ ...config, ...partial });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Featured Products</h3>

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="feat-title">Section Title</Label>
        <Input
          id="feat-title"
          value={config.title}
          onChange={(e) => update({ title: e.target.value.slice(0, 50) })}
          placeholder="Featured Products"
          maxLength={50}
        />
        <p className="text-xs text-muted-foreground">{config.title.length}/50 characters</p>
      </div>

      {/* Product Count */}
      <div className="space-y-2">
        <Label>Product Count</Label>
        <Select
          value={String(config.productCount)}
          onValueChange={(v) => update({ productCount: Number(v) as 4 | 6 | 8 })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="4">4 products</SelectItem>
            <SelectItem value="6">6 products</SelectItem>
            <SelectItem value="8">8 products</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Layout */}
      <div className="space-y-2">
        <Label>Layout</Label>
        <Select
          value={config.layout}
          onValueChange={(v) => update({ layout: v as 'grid' | 'carousel' })}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="grid">Grid</SelectItem>
            <SelectItem value="carousel">Carousel</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Display options */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium">Display Options</h4>
        <div className="flex items-center justify-between">
          <Label htmlFor="feat-price">Show Price</Label>
          <Switch
            id="feat-price"
            checked={config.showPrice}
            onCheckedChange={(v) => update({ showPrice: v })}
          />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="feat-cart">Show Add to Cart</Label>
          <Switch
            id="feat-cart"
            checked={config.showAddToCart}
            onCheckedChange={(v) => update({ showAddToCart: v })}
          />
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="feat-rating">Show Rating</Label>
          <Switch
            id="feat-rating"
            checked={config.showRating}
            onCheckedChange={(v) => update({ showRating: v })}
          />
        </div>
      </div>
    </div>
  );
}
