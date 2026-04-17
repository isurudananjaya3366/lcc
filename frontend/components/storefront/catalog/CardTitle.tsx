import Link from 'next/link';
import { cn } from '@/lib/utils';

interface CardTitleProps {
  title: string;
  productSlug: string;
  className?: string;
}

export function CardTitle({ title, productSlug, className }: CardTitleProps) {
  return (
    <h3 className={cn('text-sm font-semibold text-gray-900 leading-snug', className)}>
      <Link
        href={`/products/${productSlug}`}
        className="line-clamp-2 hover:text-blue-600 transition-colors"
      >
        {title}
      </Link>
    </h3>
  );
}
