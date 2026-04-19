'use client';

import React, { useState, useCallback } from 'react';
import { Eye, PanelLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SectionList } from './SectionList';
import { SectionSettings } from './SectionSettings';
import { AddSection } from './AddSection';
import { SaveSectionOrder } from './SaveSectionOrder';
import { HomepagePreview } from './HomepagePreview';
import { useTheme } from '@/hooks/storefront/useTheme';
import type { HomepageSection } from './types';

export interface HomepageBuilderProps {
  initialSections?: HomepageSection[];
  onSave?: (sections: HomepageSection[]) => Promise<void>;
}

export function HomepageBuilder({ initialSections = [], onSave }: HomepageBuilderProps) {
  const { updateTheme } = useTheme();

  const [sections, setSections] = useState<HomepageSection[]>(initialSections);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  const selectedSection = sections.find((s) => s.id === selectedId) ?? null;

  // --- handlers ---

  const handleReorder = useCallback((updated: HomepageSection[]) => {
    setSections(updated);
    setHasUnsavedChanges(true);
  }, []);

  const handleToggle = useCallback((id: string, enabled: boolean) => {
    setSections((prev) => prev.map((s) => (s.id === id ? { ...s, enabled } : s)));
    setHasUnsavedChanges(true);
  }, []);

  const handleSelect = useCallback((id: string) => {
    setSelectedId((prev) => (prev === id ? null : id));
    setPreviewMode(false);
  }, []);

  const handleSettingsChange = useCallback(
    (settings: Record<string, unknown>) => {
      if (!selectedId) return;
      setSections((prev) => prev.map((s) => (s.id === selectedId ? { ...s, settings } : s)));
      setHasUnsavedChanges(true);
    },
    [selectedId]
  );

  const handleAddSection = useCallback((section: HomepageSection) => {
    setSections((prev) => [...prev, { ...section, order: prev.length }]);
    setHasUnsavedChanges(true);
  }, []);

  const handleSave = async (secs: HomepageSection[]) => {
    if (onSave) {
      await onSave(secs);
    } else {
      await updateTheme({ homepage: { sections: secs } as any });
    }
    setHasUnsavedChanges(false);
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-semibold">Homepage Builder</h2>
          {hasUnsavedChanges && (
            <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded-full">
              Unsaved
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setPreviewMode((p) => !p);
              setSelectedId(null);
            }}
          >
            {previewMode ? (
              <>
                <PanelLeft className="h-4 w-4 mr-2" />
                Builder
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </>
            )}
          </Button>
          <SaveSectionOrder sections={sections} onSave={handleSave} disabled={!hasUnsavedChanges} />
        </div>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-[340px_1fr] gap-6">
        {/* Left: section list */}
        <div className="space-y-3">
          <SectionList
            sections={sections}
            selectedId={selectedId}
            onReorder={handleReorder}
            onToggle={handleToggle}
            onSelect={handleSelect}
          />
          <AddSection existingTypes={sections.map((s) => s.type)} onAdd={handleAddSection} />
        </div>

        {/* Right: config or preview */}
        <div className="border rounded-lg p-4 min-h-[300px]">
          {previewMode ? (
            <HomepagePreview sections={sections} />
          ) : selectedSection ? (
            <SectionSettings section={selectedSection} onChange={handleSettingsChange} />
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
              Select a section to configure, or switch to Preview mode.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
