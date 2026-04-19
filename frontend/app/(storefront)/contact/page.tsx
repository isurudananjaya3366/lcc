import type { Metadata } from 'next';

import { ContactPage } from '@/components/storefront/cms/Contact';

export const metadata: Metadata = {
  title: 'Contact Us',
  description: 'Get in touch with LankaCommerce. We are here to help.',
};

export default function ContactRoute() {
  return <ContactPage />;
}
