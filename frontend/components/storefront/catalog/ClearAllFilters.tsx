import { cn } from '@/lib/utils';

interface ClearAllFiltersProps {
  onClear: () => void;
  hasActiveFilters: boolean;
  className?: string;
}

export function ClearAllFilters({ onClear, hasActiveFilters, className }: ClearAllFiltersProps) {
  if (!hasActiveFilters) return null;

  return (
    <button
      type="button"
      onClick={onClear}
      className={cn(
        'inline-flex items-center gap-1 text-sm font-medium text-red-600 hover:text-red-700 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-red-500 focus-visible:ring-offset-1 rounded',
        className
      )}
    >
      {/* X icon */}
      <svg className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
        <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
      </svg>
      Clear All Filters
    </button>
  );
}
