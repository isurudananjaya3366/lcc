'use client';

import { useState, useCallback } from 'react';
import { cn } from '@/lib/utils';
import type { StoreCategory } from '@/types/store/category';

interface CategoryFilterProps {
  categories: StoreCategory[];
  selected: string[];
  onChange: (selected: string[]) => void;
}

interface CategoryTreeNode {
  category: StoreCategory;
  children: CategoryTreeNode[];
}

function buildTree(categories: StoreCategory[]): CategoryTreeNode[] {
  const map = new Map<string, CategoryTreeNode>();
  const roots: CategoryTreeNode[] = [];

  for (const cat of categories) {
    map.set(cat.id, { category: cat, children: [] });
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

function getAllDescendantIds(node: CategoryTreeNode): string[] {
  const ids: string[] = [];
  for (const child of node.children) {
    ids.push(child.category.id);
    ids.push(...getAllDescendantIds(child));
  }
  return ids;
}

export function CategoryFilter({ categories, selected, onChange }: CategoryFilterProps) {
  const tree = buildTree(categories);

  const toggleCategory = useCallback(
    (id: string, node: CategoryTreeNode) => {
      const isSelected = selected.includes(id);
      const descendantIds = getAllDescendantIds(node);

      if (isSelected) {
        // Remove this category and all descendants
        const toRemove = new Set([id, ...descendantIds]);
        onChange(selected.filter((s) => !toRemove.has(s)));
      } else {
        // Add this category and all descendants
        const newSelected = new Set([...selected, id, ...descendantIds]);
        onChange(Array.from(newSelected));
      }
    },
    [selected, onChange]
  );

  return (
    <div className="space-y-1">
      {tree.map((node) => (
        <CategoryNode
          key={node.category.id}
          node={node}
          selected={selected}
          onToggle={toggleCategory}
          depth={0}
        />
      ))}
    </div>
  );
}

interface CategoryNodeProps {
  node: CategoryTreeNode;
  selected: string[];
  onToggle: (id: string, node: CategoryTreeNode) => void;
  depth: number;
}

function CategoryNode({ node, selected, onToggle, depth }: CategoryNodeProps) {
  const [expanded, setExpanded] = useState(depth < 1);
  const { category, children } = node;
  const isSelected = selected.includes(category.id);
  const hasChildren = children.length > 0;

  // Indeterminate: some but not all descendants selected
  const descendantIds = getAllDescendantIds(node);
  const selectedDescendants = descendantIds.filter((id) => selected.includes(id));
  const isIndeterminate =
    hasChildren &&
    !isSelected &&
    selectedDescendants.length > 0 &&
    selectedDescendants.length < descendantIds.length;

  return (
    <div style={{ paddingLeft: depth * 16 }}>
      <div className="flex items-center gap-2 py-1 group">
        {hasChildren && (
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="flex-shrink-0 p-0.5 rounded hover:bg-gray-100 transition-colors"
            aria-label={expanded ? 'Collapse' : 'Expand'}
          >
            <svg
              className={cn(
                'h-3 w-3 text-gray-400 transition-transform duration-200',
                expanded && 'rotate-90'
              )}
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M7.21 14.77a.75.75 0 0 1 .02-1.06L11.168 10 7.23 6.29a.75.75 0 1 1 1.04-1.08l4.5 4.25a.75.75 0 0 1 0 1.08l-4.5 4.25a.75.75 0 0 1-1.06-.02Z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
        {!hasChildren && <span className="w-4 flex-shrink-0" />}

        <label className="flex flex-1 items-center gap-2 cursor-pointer text-sm text-gray-700 hover:text-gray-900 select-none">
          <input
            type="checkbox"
            checked={isSelected || isIndeterminate}
            ref={(el) => {
              if (el) el.indeterminate = isIndeterminate;
            }}
            onChange={() => onToggle(category.id, node)}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span>{category.name}</span>
          <span className="ml-auto text-xs text-gray-400">{category.productCount}</span>
        </label>
      </div>

      {hasChildren && expanded && (
        <div>
          {children.map((child) => (
            <CategoryNode
              key={child.category.id}
              node={child}
              selected={selected}
              onToggle={onToggle}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
