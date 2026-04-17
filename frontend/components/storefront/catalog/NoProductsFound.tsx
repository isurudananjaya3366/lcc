'use client';

import { cn } from '@/lib/utils';
import Link from 'next/link';
import { EmptyState } from './EmptyState';
import { EmptyStateIllustration } from './EmptyStateIllustration';
import { SuggestionLinks } from './SuggestionLinks';

interface NoProductsFoundProps {
  onClearFilters?: () => void;
  className?: string;
}

export function NoProductsFound({ onClearFilters, className }: NoProductsFoundProps) {
  return (
    <EmptyState
      icon={<EmptyStateIllustration variant="filter" size={100} />}
      title="No products found"
      description="Try adjusting your filters or search terms to find what you&rsquo;re looking for."
      action={onClearFilters ? { label: 'Clear All Filters', onClick: onClearFilters } : undefined}
      secondaryAction={{ label: 'Browse All Products', href: '/products' }}
      className={className}
    >
      <SuggestionLinks variant="filter" className="mt-2" />
    </EmptyState>
  );
}
