'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { BlogCategory } from '@/types/storefront/cms.types';

interface BlogCategoriesProps {
  categories: BlogCategory[];
  selected: string;
  onSelect: (slug: string) => void;
}

export function BlogCategories({ categories, selected, onSelect }: BlogCategoriesProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
      <Button
        variant={selected === '' ? 'default' : 'outline'}
        size="sm"
        onClick={() => onSelect('')}
        className={cn('shrink-0')}
      >
        All
      </Button>
      {categories.map((cat) => (
        <Button
          key={cat.id}
          variant={selected === cat.slug ? 'default' : 'outline'}
          size="sm"
          onClick={() => onSelect(cat.slug)}
          className={cn('shrink-0')}
        >
          {cat.name}
          {cat.postCount != null && (
            <Badge variant="secondary" className="ml-1.5 px-1.5 py-0 text-xs">
              {cat.postCount}
            </Badge>
          )}
        </Button>
      ))}
    </div>
  );
}
