'use client';

import { useMemo } from 'react';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface Category {
  id: string;
  name: string;
  parentId: string | null;
  children?: Category[];
}

interface ParentCategorySelectProps {
  value: string | null;
  onChange: (categoryId: string | null) => void;
  currentCategoryId?: string;
  categories: Category[];
  disabled?: boolean;
  error?: string;
}

function getDescendantIds(categories: Category[], id: string): Set<string> {
  const ids = new Set<string>();
  function collect(cats: Category[]) {
    for (const cat of cats) {
      if (cat.id === id || ids.has(cat.parentId || '')) {
        ids.add(cat.id);
      }
      if (cat.children) collect(cat.children);
    }
  }
  collect(categories);
  return ids;
}

function flattenCategories(
  categories: Category[],
  depth = 0
): Array<{ id: string; name: string; depth: number; parentId: string | null }> {
  const result: Array<{ id: string; name: string; depth: number; parentId: string | null }> = [];
  for (const cat of categories) {
    result.push({ id: cat.id, name: cat.name, depth, parentId: cat.parentId });
    if (cat.children) {
      result.push(...flattenCategories(cat.children, depth + 1));
    }
  }
  return result;
}

function buildTree(categories: Category[]): Category[] {
  const map = new Map<string, Category & { children: Category[] }>();
  const roots: Category[] = [];

  for (const cat of categories) {
    map.set(cat.id, { ...cat, children: [] });
  }

  for (const cat of categories) {
    const node = map.get(cat.id)!;
    if (cat.parentId && map.has(cat.parentId)) {
      map.get(cat.parentId)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

export function ParentCategorySelect({
  value,
  onChange,
  currentCategoryId,
  categories,
  disabled,
  error,
}: ParentCategorySelectProps) {
  const tree = useMemo(() => buildTree(categories), [categories]);
  const flatList = useMemo(() => flattenCategories(tree), [tree]);

  const disabledIds = useMemo(() => {
    if (!currentCategoryId) return new Set<string>();
    const descendants = getDescendantIds(categories, currentCategoryId);
    descendants.add(currentCategoryId);
    return descendants;
  }, [categories, currentCategoryId]);

  return (
    <div className="space-y-2">
      <Label>Parent Category</Label>
      <Select
        value={value || 'none'}
        onValueChange={(v) => onChange(v === 'none' ? null : v)}
        disabled={disabled}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select parent category..." />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="none">No Parent (Root Level)</SelectItem>
          {flatList.map((cat) => (
            <SelectItem key={cat.id} value={cat.id} disabled={disabledIds.has(cat.id)}>
              {'—'.repeat(cat.depth)} {cat.depth > 0 ? ' ' : ''}
              {cat.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
