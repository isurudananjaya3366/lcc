'use client';

import React from 'react';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Plus, Trash2, Star } from 'lucide-react';

export interface TestimonialItem {
  id: string;
  name: string;
  text: string;
  rating: number;
}

export interface TestimonialsSettings {
  title: string;
  items: TestimonialItem[];
}

export interface TestimonialsConfigProps {
  config: TestimonialsSettings;
  onChange: (config: TestimonialsSettings) => void;
}

const DEFAULTS: TestimonialsSettings = {
  title: 'What Our Customers Say',
  items: [],
};

function generateId() {
  return Math.random().toString(36).substring(2, 9);
}

export function TestimonialsConfig({ config = DEFAULTS, onChange }: TestimonialsConfigProps) {
  const update = (partial: Partial<TestimonialsSettings>) => {
    onChange({ ...config, ...partial });
  };

  const updateItem = (id: string, partial: Partial<TestimonialItem>) => {
    const items = config.items.map((item) => (item.id === id ? { ...item, ...partial } : item));
    update({ items });
  };

  const addItem = () => {
    update({
      items: [...config.items, { id: generateId(), name: '', text: '', rating: 5 }],
    });
  };

  const removeItem = (id: string) => {
    update({ items: config.items.filter((item) => item.id !== id) });
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold">Testimonials</h3>

      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="test-title">Section Title</Label>
        <Input
          id="test-title"
          value={config.title}
          onChange={(e) => update({ title: e.target.value.slice(0, 50) })}
          placeholder="What Our Customers Say"
          maxLength={50}
        />
        <p className="text-xs text-muted-foreground">{config.title.length}/50 characters</p>
      </div>

      {/* Items */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium">Testimonials ({config.items.length})</h4>

        {config.items.map((item, index) => (
          <div key={item.id} className="border rounded-lg p-4 space-y-3 bg-muted/30">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">#{index + 1}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => removeItem(item.id)}
                aria-label="Remove testimonial"
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>

            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={item.name}
                onChange={(e) => updateItem(item.id, { name: e.target.value })}
                placeholder="Customer name"
              />
            </div>

            <div className="space-y-2">
              <Label>Testimonial</Label>
              <Textarea
                value={item.text}
                onChange={(e) => updateItem(item.id, { text: e.target.value })}
                placeholder="What they said..."
                rows={2}
              />
            </div>

            <div className="space-y-2">
              <Label>Rating</Label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => updateItem(item.id, { rating: star })}
                    className="p-0.5"
                    aria-label={`${star} star${star > 1 ? 's' : ''}`}
                  >
                    <Star
                      className={`h-5 w-5 ${
                        star <= item.rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-muted-foreground'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}

        <Button variant="outline" size="sm" onClick={addItem} className="w-full">
          <Plus className="h-4 w-4 mr-2" />
          Add Testimonial
        </Button>
      </div>
    </div>
  );
}
