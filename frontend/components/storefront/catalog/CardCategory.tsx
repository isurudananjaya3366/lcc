import Link from 'next/link';
import { cn } from '@/lib/utils';

interface CardCategoryProps {
  categoryName: string;
  categorySlug: string;
  className?: string;
}

export function CardCategory({ categoryName, categorySlug, className }: CardCategoryProps) {
  return (
    <Link
      href={`/products/category/${categorySlug}`}
      onClick={(e) => e.stopPropagation()}
      className={cn(
        'text-xs font-medium text-gray-500 hover:text-blue-600 transition-colors',
        className
      )}
    >
      {categoryName}
    </Link>
  );
}
