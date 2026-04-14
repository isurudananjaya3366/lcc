import type { Metadata } from 'next';
import { OrderDetail } from '@/components/modules/sales/Orders/OrderDetail';

export const metadata: Metadata = {
  title: 'Order Details - LCC',
  description: 'View order details, items, timeline, and shipping information',
  openGraph: {
    title: 'Order Details - LCC',
    description: 'View order details, items, timeline, and shipping information',
    type: 'website',
  },
};

interface OrderDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function OrderDetailPage({ params }: OrderDetailPageProps) {
  const { id } = await params;
  return <OrderDetail orderId={id} />;
}
