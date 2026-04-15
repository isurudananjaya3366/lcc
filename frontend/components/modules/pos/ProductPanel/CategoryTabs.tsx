'use client';

interface CategoryTabsProps {
  categories: Array<{ id: string; name: string }>;
  activeId: string;
  onSelect: (id: string) => void;
}

export function CategoryTabs({ categories, activeId, onSelect }: CategoryTabsProps) {
  return (
    <div className="flex gap-1 overflow-x-auto pb-1" role="tablist" aria-label="Product categories">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.id)}
          role="tab"
          aria-selected={cat.id === activeId}
          className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${
            cat.id === activeId
              ? 'bg-primary text-primary-foreground'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          {cat.name}
        </button>
      ))}
    </div>
  );
}
