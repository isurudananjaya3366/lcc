import type { Metadata } from 'next';
import { WishlistPage } from '@/components/storefront/portal/Wishlist';

export const metadata: Metadata = {
  title: 'My Wishlist',
};

export default function WishlistRoute() {
  return <WishlistPage />;
}
