import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Shopping Cart',
  description: 'Review your cart and proceed to checkout.',
};

/**
 * Shopping cart page — shows cart items, totals, checkout button.
 * Will be fully implemented in SubPhase-06.
 */
export default function CartPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Shopping Cart</h1>
      <p className="text-muted-foreground">Shopping cart will be implemented in SubPhase-06.</p>
    </div>
  );
}
