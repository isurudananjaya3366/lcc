import { cn } from '@/lib/utils';
import type { StoreProduct } from '@/types/store/product';
import { CardCategory } from './CardCategory';
import { CardTitle } from './CardTitle';
import { CardRating } from './CardRating';
import { CardPrice } from './CardPrice';

interface CardContentProps {
  product: StoreProduct;
  className?: string;
}

export function CardContent({ product, className }: CardContentProps) {
  return (
    <div className={cn('p-3 space-y-1.5', className)}>
      <CardCategory categoryName={product.categoryName} categorySlug={product.categorySlug} />
      <CardTitle title={product.name} productSlug={product.slug} />
      <CardRating rating={product.rating} reviewCount={product.reviewCount} />
      <CardPrice
        price={product.price}
        compareAtPrice={product.compareAtPrice}
        currency={product.currency}
      />
    </div>
  );
}
