import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Account',
  description: 'Manage your account, orders, and preferences.',
};

/**
 * Customer account page — profile, orders, addresses, wishlist.
 * Will be fully implemented in SubPhase-10.
 */
export default function AccountPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">My Account</h1>
      <p className="text-muted-foreground">
        Account management will be implemented in SubPhase-10.
      </p>
    </div>
  );
}
