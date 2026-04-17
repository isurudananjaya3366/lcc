import { cn } from '@/lib/utils';
import { EmptyState } from './EmptyState';
import { EmptyStateIllustration } from './EmptyStateIllustration';
import { SuggestionLinks } from './SuggestionLinks';

interface NoSearchResultsProps {
  query: string;
  onClearSearch?: () => void;
  className?: string;
}

export function NoSearchResults({ query, onClearSearch, className }: NoSearchResultsProps) {
  return (
    <EmptyState
      icon={<EmptyStateIllustration variant="search" size={100} />}
      title="No results found"
      description={`We couldn\u2019t find any products matching \u201c${query}\u201d.`}
      action={onClearSearch ? { label: 'Clear Search', onClick: onClearSearch } : undefined}
      secondaryAction={{ label: 'Browse All Products', href: '/products' }}
      className={className}
    >
      <div className="mt-2 text-sm text-gray-500">
        <p className="font-medium text-gray-700 mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-0.5 text-left">
          <li>Check the spelling of your search term</li>
          <li>Try using more general keywords</li>
          <li>Try searching for a related term</li>
        </ul>
      </div>
      <SuggestionLinks variant="search" className="mt-3" />
    </EmptyState>
  );
}
