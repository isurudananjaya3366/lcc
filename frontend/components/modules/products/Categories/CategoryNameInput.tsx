'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Lock, Unlock } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface CategoryNameInputProps {
  name: string;
  slug: string;
  onNameChange: (name: string) => void;
  onSlugChange: (slug: string) => void;
  existingSlugs?: string[];
  error?: string;
}

function generateSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

export function CategoryNameInput({
  name,
  slug,
  onNameChange,
  onSlugChange,
  existingSlugs = [],
  error,
}: CategoryNameInputProps) {
  const [slugLocked, setSlugLocked] = useState(true);

  useEffect(() => {
    if (slugLocked) {
      onSlugChange(generateSlug(name));
    }
  }, [name, slugLocked, onSlugChange]);

  const slugError =
    slug && existingSlugs.some((s) => s === slug) ? 'This URL slug is already in use' : undefined;

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="category-name">
          Name <span className="text-red-500">*</span>
        </Label>
        <Input
          id="category-name"
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="e.g. Men's Clothing"
          maxLength={100}
        />
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label htmlFor="category-slug">
            URL Slug <span className="text-red-500">*</span>
          </Label>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-6 gap-1 text-xs"
            onClick={() => setSlugLocked(!slugLocked)}
          >
            {slugLocked ? (
              <>
                <Lock className="h-3 w-3" /> Auto
              </>
            ) : (
              <>
                <Unlock className="h-3 w-3" /> Manual
              </>
            )}
          </Button>
        </div>
        <Input
          id="category-slug"
          value={slug}
          onChange={(e) => {
            if (!slugLocked) {
              const sanitized = e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '');
              onSlugChange(sanitized);
            }
          }}
          readOnly={slugLocked}
          className={slugLocked ? 'bg-gray-50 dark:bg-gray-800' : ''}
          placeholder="url-slug"
        />
        {slug && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Preview: /products/category/{slug}
          </p>
        )}
        {(slugError || error) && <p className="text-xs text-red-500">{slugError || error}</p>}
      </div>
    </div>
  );
}
