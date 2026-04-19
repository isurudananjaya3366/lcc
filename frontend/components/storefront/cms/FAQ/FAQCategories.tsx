'use client';

import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

interface FAQCategoriesProps {
  categories: string[];
  selected: string;
  onSelect: (c: string) => void;
}

export function FAQCategories({ categories, selected, onSelect }: FAQCategoriesProps) {
  return (
    <div className="mb-6 flex flex-wrap gap-2">
      <Badge
        variant={selected === 'All' ? 'default' : 'outline'}
        className={cn('cursor-pointer', selected === 'All' && 'bg-primary text-primary-foreground')}
        onClick={() => onSelect('All')}
      >
        All
      </Badge>
      {categories.map((cat) => (
        <Badge
          key={cat}
          variant={selected === cat ? 'default' : 'outline'}
          className={cn('cursor-pointer', selected === cat && 'bg-primary text-primary-foreground')}
          onClick={() => onSelect(cat)}
        >
          {cat}
        </Badge>
      ))}
    </div>
  );
}
