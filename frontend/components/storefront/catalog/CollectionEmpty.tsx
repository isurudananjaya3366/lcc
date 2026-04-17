import { cn } from '@/lib/utils';
import { EmptyState } from './EmptyState';
import { EmptyStateIllustration } from './EmptyStateIllustration';

interface CollectionEmptyProps {
  collectionName?: string;
  className?: string;
}

export function CollectionEmpty({ collectionName, className }: CollectionEmptyProps) {
  const title = collectionName
    ? `No products in "${collectionName}"`
    : 'No products in this collection';

  return (
    <EmptyState
      icon={<EmptyStateIllustration variant="empty" size={100} />}
      title={title}
      description="This collection is currently empty. Browse our other collections or check back soon."
      action={{ label: 'Browse All Products', href: '/products' }}
      secondaryAction={{ label: 'View Collections', href: '/collections' }}
      className={className}
    />
  );
}
