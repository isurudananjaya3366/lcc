import type { Metadata } from 'next';
import { ReturnsPage } from '@/components/storefront/cms/Policy';

export const metadata: Metadata = {
  title: 'Return Policy',
};

export default function ReturnsRoute() {
  return <ReturnsPage />;
}
