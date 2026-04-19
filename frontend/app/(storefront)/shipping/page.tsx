import type { Metadata } from 'next';
import { ShippingPage } from '@/components/storefront/cms/Policy';

export const metadata: Metadata = {
  title: 'Shipping Information',
};

export default function ShippingRoute() {
  return <ShippingPage />;
}
