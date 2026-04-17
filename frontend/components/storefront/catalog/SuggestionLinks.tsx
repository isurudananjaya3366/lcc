import { cn } from '@/lib/utils';
import Link from 'next/link';

type SuggestionVariant = 'search' | 'filter' | 'category';

interface Suggestion {
  label: string;
  href: string;
}

interface SuggestionLinksProps {
  variant?: SuggestionVariant;
  suggestions?: Suggestion[];
  className?: string;
}

const defaultSuggestions: Record<SuggestionVariant, Suggestion[]> = {
  search: [
    { label: 'New Arrivals', href: '/products?sort=newest' },
    { label: 'Best Sellers', href: '/products?sort=best-selling' },
    { label: 'On Sale', href: '/products?on_sale=true' },
  ],
  filter: [
    { label: 'New Arrivals', href: '/products?sort=newest' },
    { label: 'Popular Products', href: '/products?sort=popular' },
    { label: 'All Categories', href: '/categories' },
  ],
  category: [
    { label: 'Browse All Products', href: '/products' },
    { label: 'View Collections', href: '/collections' },
    { label: 'New Arrivals', href: '/products?sort=newest' },
  ],
};

export function SuggestionLinks({
  variant = 'search',
  suggestions,
  className,
}: SuggestionLinksProps) {
  const links = suggestions ?? defaultSuggestions[variant];

  if (links.length === 0) return null;

  return (
    <div className={cn('flex flex-wrap items-center justify-center gap-2', className)}>
      <span className="text-xs text-gray-400">Try:</span>
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="inline-flex items-center gap-1 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors"
        >
          {/* Arrow icon */}
          <svg
            width="12"
            height="12"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
          {link.label}
        </Link>
      ))}
    </div>
  );
}
