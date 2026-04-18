import type { Metadata } from 'next';
import { ReviewsPage } from '@/components/storefront/portal/Reviews';

export const metadata: Metadata = {
  title: 'My Reviews',
};

export default function ReviewsRoute() {
  return <ReviewsPage />;
}
