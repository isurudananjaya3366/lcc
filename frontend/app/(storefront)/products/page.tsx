import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Products',
  description: 'Browse our full catalog of quality products. Filter by category, price, and more.',
};

/**
 * Product listing page — shows all products with filtering/sorting.
 * Will be fully implemented in SubPhase-03.
 */
export default function ProductsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">All Products</h1>
      <p className="text-muted-foreground">Product listing will be implemented in SubPhase-03.</p>
    </div>
  );
}
