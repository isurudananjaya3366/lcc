'use client';

import React from 'react';
import { Image, ShoppingBag, LayoutGrid, MessageSquare, Mail, EyeOff } from 'lucide-react';
import { SECTION_TYPE_LABELS } from './types';
import type { HomepageSection, SectionType } from './types';
import { cn } from '@/lib/utils';

export interface HomepagePreviewProps {
  sections: HomepageSection[];
}

const SECTION_ICONS: Record<SectionType, React.ReactNode> = {
  hero: <Image className="h-6 w-6" />,
  featured: <ShoppingBag className="h-6 w-6" />,
  categories: <LayoutGrid className="h-6 w-6" />,
  testimonials: <MessageSquare className="h-6 w-6" />,
  newsletter: <Mail className="h-6 w-6" />,
};

const SECTION_HEIGHTS: Record<SectionType, string> = {
  hero: 'h-32',
  featured: 'h-24',
  categories: 'h-20',
  testimonials: 'h-20',
  newsletter: 'h-16',
};

export function HomepagePreview({ sections }: HomepagePreviewProps) {
  const sorted = [...sections].sort((a, b) => a.order - b.order);

  if (sorted.length === 0) {
    return (
      <div className="border rounded-lg p-8 text-center text-muted-foreground">
        <p className="text-sm">No sections to preview.</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-muted-foreground">Homepage Preview</h3>
      <div className="border rounded-lg overflow-hidden bg-background">
        {sorted.map((section) => {
          const type = section.type as SectionType;
          const label = SECTION_TYPE_LABELS[type] ?? section.type;
          const icon = SECTION_ICONS[type];
          const height = SECTION_HEIGHTS[type] ?? 'h-20';

          return (
            <div
              key={section.id}
              className={cn(
                'flex items-center justify-center gap-2 border-b last:border-b-0 transition-opacity',
                height,
                section.enabled ? 'bg-muted/20' : 'bg-muted/5 opacity-40'
              )}
            >
              {section.enabled ? (
                <>
                  <span className="text-muted-foreground">{icon}</span>
                  <span className="text-sm font-medium">{label}</span>
                </>
              ) : (
                <>
                  <EyeOff className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground line-through">{label}</span>
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
