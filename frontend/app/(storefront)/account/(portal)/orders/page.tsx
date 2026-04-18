import type { Metadata } from 'next';
import { OrdersPage } from '@/components/storefront/portal/Orders';

export const metadata: Metadata = {
  title: 'My Orders',
};

export default function OrdersRoute() {
  return <OrdersPage />;
}
