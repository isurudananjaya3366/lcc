'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Plus, Image, ShoppingBag, LayoutGrid, MessageSquare, Mail } from 'lucide-react';
import { SECTION_TYPE_LABELS, SECTION_TYPE_DEFAULTS } from './types';
import type { SectionType, HomepageSection } from './types';

export interface AddSectionProps {
  existingTypes: string[];
  onAdd: (section: HomepageSection) => void;
}

const SECTION_ICONS: Record<SectionType, React.ReactNode> = {
  hero: <Image className="h-5 w-5" />,
  featured: <ShoppingBag className="h-5 w-5" />,
  categories: <LayoutGrid className="h-5 w-5" />,
  testimonials: <MessageSquare className="h-5 w-5" />,
  newsletter: <Mail className="h-5 w-5" />,
};

const ALL_TYPES: SectionType[] = ['hero', 'featured', 'categories', 'testimonials', 'newsletter'];

function generateId() {
  return Math.random().toString(36).substring(2, 9);
}

export function AddSection({ existingTypes, onAdd }: AddSectionProps) {
  const [open, setOpen] = useState(false);

  const availableTypes = ALL_TYPES.filter((t) => !existingTypes.includes(t));

  const handleAdd = (type: SectionType) => {
    const section: HomepageSection = {
      id: generateId(),
      type,
      enabled: true,
      order: existingTypes.length,
      settings: { ...SECTION_TYPE_DEFAULTS[type] },
    };
    onAdd(section);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="w-full"
          disabled={availableTypes.length === 0}
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Section
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add Homepage Section</DialogTitle>
        </DialogHeader>
        <div className="space-y-2 pt-2">
          {availableTypes.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              All section types have been added.
            </p>
          ) : (
            availableTypes.map((type) => (
              <button
                key={type}
                onClick={() => handleAdd(type)}
                className="w-full flex items-center gap-3 rounded-lg border p-3 hover:bg-muted transition-colors text-left"
              >
                <span className="text-muted-foreground">{SECTION_ICONS[type]}</span>
                <span className="font-medium text-sm">{SECTION_TYPE_LABELS[type]}</span>
              </button>
            ))
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
