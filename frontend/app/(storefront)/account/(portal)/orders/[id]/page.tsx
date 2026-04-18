import type { Metadata } from 'next';
import { OrderDetailPage } from '@/components/storefront/portal/Orders';

export const metadata: Metadata = {
  title: 'Order Details',
};

export default function OrderDetailRoute({ params }: { params: { id: string } }) {
  return <OrderDetailPage orderId={params.id} />;
}
