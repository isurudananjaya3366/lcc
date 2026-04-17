import { cn } from '@/lib/utils';
import { EmptyState } from './EmptyState';
import { EmptyStateIllustration } from './EmptyStateIllustration';

interface CategoryEmptyProps {
  categoryName?: string;
  className?: string;
}

export function CategoryEmpty({ categoryName, className }: CategoryEmptyProps) {
  const title = categoryName ? `No products in "${categoryName}"` : 'No products in this category';

  return (
    <EmptyState
      icon={<EmptyStateIllustration variant="empty" size={100} />}
      title={title}
      description="This category doesn&rsquo;t have any products yet. Check back later or browse other categories."
      action={{ label: 'Browse All Products', href: '/products' }}
      secondaryAction={{ label: 'View Categories', href: '/categories' }}
      className={className}
    />
  );
}
