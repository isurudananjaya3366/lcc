import type { Product } from '@/lib/api/store/modules/products';
import { RelatedProductCard } from './RelatedProductCard';

interface CrossSellSectionProps {
  products: Product[];
}

export function CrossSellSection({ products }: CrossSellSectionProps) {
  if (products.length === 0) return null;

  return (
    <section aria-label="Frequently bought together">
      <h2 className="mb-4 text-lg font-bold text-gray-900">Frequently Bought Together</h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {products.map((product) => (
          <RelatedProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}
