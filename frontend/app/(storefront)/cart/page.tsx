import type { Metadata } from 'next';
import { CartPageContainer } from '@/components/storefront/cart/CartPage';

export const metadata: Metadata = {
  title: 'Shopping Cart | LankaCommerce Store',
  description: 'Review your shopping cart and proceed to checkout.',
};

export default function CartPage() {
  return <CartPageContainer />;
}
