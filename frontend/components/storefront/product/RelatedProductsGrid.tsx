import type { Product } from '@/lib/api/store/modules/products';
import { RelatedProductCard } from './RelatedProductCard';

interface RelatedProductsGridProps {
  products: Product[];
}

export function RelatedProductsGrid({ products }: RelatedProductsGridProps) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
      {products.map((product) => (
        <RelatedProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}
