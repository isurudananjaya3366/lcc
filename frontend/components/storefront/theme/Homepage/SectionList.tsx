'use client';

import React from 'react';
import { ChevronUp, ChevronDown, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SectionDragHandle } from './SectionDragHandle';
import { SectionToggle } from './SectionToggle';
import { SECTION_TYPE_LABELS } from './types';
import type { HomepageSection, SectionType } from './types';
import { cn } from '@/lib/utils';

export interface SectionListProps {
  sections: HomepageSection[];
  selectedId: string | null;
  onReorder: (sections: HomepageSection[]) => void;
  onToggle: (id: string, enabled: boolean) => void;
  onSelect: (id: string) => void;
}

export function SectionList({
  sections,
  selectedId,
  onReorder,
  onToggle,
  onSelect,
}: SectionListProps) {
  const moveUp = (index: number) => {
    if (index === 0) return;
    const updated = [...sections];
    [updated[index - 1], updated[index]] = [updated[index]!, updated[index - 1]!];
    onReorder(updated.map((s, i) => ({ ...s, order: i })));
  };

  const moveDown = (index: number) => {
    if (index === sections.length - 1) return;
    const updated = [...sections];
    [updated[index], updated[index + 1]] = [updated[index + 1]!, updated[index]!];
    onReorder(updated.map((s, i) => ({ ...s, order: i })));
  };

  const enabledCount = sections.filter((s) => s.enabled).length;

  if (sections.length === 0) {
    return (
      <div className="border rounded-lg p-6 text-center text-muted-foreground">
        <p className="text-sm">No sections added yet.</p>
        <p className="text-xs mt-1">Use &quot;Add Section&quot; to get started.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-xs text-muted-foreground px-1">
        <span>Sections ({sections.length})</span>
        <span>{enabledCount} enabled</span>
      </div>

      <div className="space-y-1">
        {sections.map((section, index) => (
          <div
            key={section.id}
            className={cn(
              'flex items-center gap-2 rounded-lg border p-2 transition-colors',
              selectedId === section.id ? 'border-primary bg-primary/5' : 'hover:bg-muted/50',
              !section.enabled && 'opacity-60'
            )}
          >
            {/* Drag handle placeholder + up/down buttons */}
            <div className="flex flex-col items-center gap-0.5">
              <SectionDragHandle />
              <div className="flex flex-col">
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5"
                  onClick={() => moveUp(index)}
                  disabled={index === 0}
                  aria-label="Move up"
                >
                  <ChevronUp className="h-3 w-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5"
                  onClick={() => moveDown(index)}
                  disabled={index === sections.length - 1}
                  aria-label="Move down"
                >
                  <ChevronDown className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Section name */}
            <span className="flex-1 text-sm font-medium truncate">
              {SECTION_TYPE_LABELS[section.type as SectionType] ?? section.type}
            </span>

            {/* Toggle */}
            <SectionToggle
              enabled={section.enabled}
              onChange={(enabled) => onToggle(section.id, enabled)}
              size="sm"
            />

            {/* Config button */}
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={() => onSelect(section.id)}
              aria-label="Configure section"
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
