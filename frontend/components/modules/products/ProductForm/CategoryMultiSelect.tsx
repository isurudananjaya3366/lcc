'use client';

import { useState, useRef } from 'react';
import { Check, ChevronDown } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';

// Placeholder categories — will be replaced with API data
const PLACEHOLDER_CATEGORIES = [
  { id: 'cat-electronics', name: 'Electronics', parentId: null },
  { id: 'cat-computers', name: 'Computers', parentId: 'cat-electronics' },
  { id: 'cat-laptops', name: 'Laptops', parentId: 'cat-computers' },
  { id: 'cat-desktops', name: 'Desktops', parentId: 'cat-computers' },
  { id: 'cat-phones', name: 'Mobile Phones', parentId: 'cat-electronics' },
  { id: 'cat-clothing', name: 'Clothing', parentId: null },
  { id: 'cat-mens', name: "Men's Wear", parentId: 'cat-clothing' },
  { id: 'cat-womens', name: "Women's Wear", parentId: 'cat-clothing' },
  { id: 'cat-home', name: 'Home & Garden', parentId: null },
  { id: 'cat-furniture', name: 'Furniture', parentId: 'cat-home' },
  { id: 'cat-kitchen', name: 'Kitchen Appliances', parentId: 'cat-home' },
];

interface CategoryNode {
  id: string;
  name: string;
  parentId: string | null;
  children: CategoryNode[];
}

function buildTree(items: { id: string; name: string; parentId: string | null }[]): CategoryNode[] {
  const map = new Map<string, CategoryNode>();
  const roots: CategoryNode[] = [];

  for (const item of items) {
    map.set(item.id, { ...item, children: [] });
  }

  for (const node of map.values()) {
    if (node.parentId && map.has(node.parentId)) {
      map.get(node.parentId)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

interface CategoryMultiSelectProps {
  value: string[];
  onChange: (value: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function CategoryMultiSelect({
  value,
  onChange,
  disabled = false,
  placeholder = 'Select categories...',
}: CategoryMultiSelectProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const searchRef = useRef<HTMLInputElement>(null);

  const categories = PLACEHOLDER_CATEGORIES;
  const tree = buildTree(categories);

  const toggleCategory = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  const selectedNames = categories.filter((c) => value.includes(c.id)).map((c) => c.name);

  const matchesSearch = (name: string) =>
    !search || name.toLowerCase().includes(search.toLowerCase());

  const renderNode = (node: CategoryNode, level: number): React.ReactNode => {
    const matches = matchesSearch(node.name);
    const childrenMatch = node.children.some(
      (c) => matchesSearch(c.name) || c.children.some((gc) => matchesSearch(gc.name))
    );

    if (!matches && !childrenMatch) return null;

    return (
      <div key={node.id}>
        <button
          type="button"
          className={cn(
            'flex w-full items-center gap-2 rounded px-2 py-1.5 text-sm hover:bg-gray-100 dark:hover:bg-gray-800',
            !matches && 'opacity-50'
          )}
          style={{ paddingLeft: `${level * 16 + 8}px` }}
          onClick={() => toggleCategory(node.id)}
        >
          <Checkbox
            checked={value.includes(node.id)}
            className="pointer-events-none"
            tabIndex={-1}
          />
          <span className="flex-1 text-left">{node.name}</span>
          {value.includes(node.id) && <Check className="h-3.5 w-3.5 text-blue-600" />}
        </button>
        {node.children.length > 0 && (
          <div>{node.children.map((child) => renderNode(child, level + 1))}</div>
        )}
      </div>
    );
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          type="button"
          variant="outline"
          role="combobox"
          aria-expanded={open}
          disabled={disabled}
          className="w-full justify-between font-normal"
        >
          {selectedNames.length === 0 && (
            <span className="text-muted-foreground">{placeholder}</span>
          )}
          {selectedNames.length === 1 && selectedNames[0]}
          {selectedNames.length > 1 && `${selectedNames.length} categories selected`}
          <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[320px] p-0" align="start">
        <div className="border-b p-2">
          <Input
            ref={searchRef}
            placeholder="Search categories..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8"
          />
        </div>
        <div className="max-h-60 overflow-y-auto p-1">
          {tree.map((node) => renderNode(node, 0))}
          {tree.every(
            (node) =>
              !matchesSearch(node.name) &&
              !node.children.some(
                (c) => matchesSearch(c.name) || c.children.some((gc) => matchesSearch(gc.name))
              )
          ) && (
            <p className="p-4 text-center text-sm text-muted-foreground">No categories found.</p>
          )}
        </div>
        {value.length > 0 && (
          <div className="flex flex-wrap gap-1 border-t p-2">
            {selectedNames.map((name, i) => (
              <Badge key={value[i]} variant="secondary" className="text-xs">
                {name}
              </Badge>
            ))}
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
