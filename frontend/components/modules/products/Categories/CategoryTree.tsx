'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronDown, ChevronRight, Circle, Edit, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface CategoryWithChildren {
  id: string;
  name: string;
  slug: string;
  productCount: number;
  isActive: boolean;
  children?: CategoryWithChildren[];
}

interface CategoryTreeProps {
  categories: CategoryWithChildren[];
  onEdit: (categoryId: string) => void;
  onDelete: (categoryId: string) => void;
  expandedByDefault?: boolean;
  maxDepth?: number;
}

function CategoryNode({
  category,
  depth,
  expanded,
  onToggle,
  onEdit,
  onDelete,
  maxDepth,
}: {
  category: CategoryWithChildren;
  depth: number;
  expanded: Set<string>;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  maxDepth: number;
}) {
  const hasChildren = category.children && category.children.length > 0;
  const isExpanded = expanded.has(category.id);
  const indentClass =
    depth === 0
      ? 'pl-0'
      : depth === 1
        ? 'pl-6'
        : depth === 2
          ? 'pl-12'
          : depth === 3
            ? 'pl-18'
            : 'pl-24';

  return (
    <div role="treeitem" aria-expanded={hasChildren ? isExpanded : undefined}>
      <div
        className={cn(
          'group flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800',
          indentClass,
          !category.isActive && 'opacity-60'
        )}
      >
        {/* Expand toggle */}
        <button
          type="button"
          className="flex h-5 w-5 shrink-0 items-center justify-center"
          onClick={() => hasChildren && onToggle(category.id)}
          aria-label={isExpanded ? 'Collapse' : 'Expand'}
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-500" />
            )
          ) : (
            <Circle className="h-2 w-2 text-gray-300 dark:text-gray-600" />
          )}
        </button>

        {/* Name */}
        <span className="flex-1 truncate text-sm font-medium text-gray-900 dark:text-gray-100">
          {category.name}
        </span>

        {/* Product count */}
        <Badge variant="secondary" className="text-xs">
          {category.productCount}
        </Badge>

        {/* Actions */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => onEdit(category.id)}
          >
            <Edit className="h-3 w-3" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 text-red-600 hover:text-red-700"
            onClick={() => onDelete(category.id)}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>
      </div>

      {/* Children */}
      {hasChildren && isExpanded && depth < maxDepth && (
        <div role="group">
          {category.children!.map((child) => (
            <CategoryNode
              key={child.id}
              category={child}
              depth={depth + 1}
              expanded={expanded}
              onToggle={onToggle}
              onEdit={onEdit}
              onDelete={onDelete}
              maxDepth={maxDepth}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function CategoryTree({
  categories,
  onEdit,
  onDelete,
  expandedByDefault = false,
  maxDepth = 5,
}: CategoryTreeProps) {
  const getAllIds = useCallback(
    (cats: CategoryWithChildren[]): string[] =>
      cats.flatMap((c) => [c.id, ...(c.children ? getAllIds(c.children) : [])]),
    []
  );

  const [expanded, setExpanded] = useState<Set<string>>(
    expandedByDefault ? new Set(getAllIds(categories)) : new Set()
  );

  const toggleExpand = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  if (categories.length === 0) {
    return (
      <div className="py-8 text-center text-sm text-gray-500 dark:text-gray-400">
        No categories found. Create your first category.
      </div>
    );
  }

  return (
    <div role="tree" className="space-y-0.5">
      {categories.map((category) => (
        <CategoryNode
          key={category.id}
          category={category}
          depth={0}
          expanded={expanded}
          onToggle={toggleExpand}
          onEdit={onEdit}
          onDelete={onDelete}
          maxDepth={maxDepth}
        />
      ))}
    </div>
  );
}
