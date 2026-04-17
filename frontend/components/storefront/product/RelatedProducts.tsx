import type { Product } from '@/lib/api/store/modules/products';
import { RelatedProductsHeader } from './RelatedProductsHeader';
import { RelatedProductsGrid } from './RelatedProductsGrid';

interface RelatedProductsProps {
  products: Product[];
  title?: string;
}

export function RelatedProducts({ products, title = 'You May Also Like' }: RelatedProductsProps) {
  if (products.length === 0) return null;

  return (
    <section aria-label="Related products">
      <RelatedProductsHeader title={title} />
      <RelatedProductsGrid products={products} />
    </section>
  );
}
