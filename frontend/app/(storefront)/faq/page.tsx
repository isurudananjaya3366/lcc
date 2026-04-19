import type { Metadata } from 'next';

import { FAQPage } from '@/components/storefront/cms/FAQ';

export const metadata: Metadata = {
  title: 'FAQ',
  description: 'Frequently asked questions about LankaCommerce.',
};

export default function FAQRoute() {
  return <FAQPage />;
}
