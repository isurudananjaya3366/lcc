import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Checkout',
  description: 'Complete your purchase securely.',
};

/**
 * Checkout page — multi-step checkout flow.
 * Will be fully implemented in SubPhase-07.
 */
export default function CheckoutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Checkout</h1>
      <p className="text-muted-foreground">Checkout flow will be implemented in SubPhase-07.</p>
    </div>
  );
}
