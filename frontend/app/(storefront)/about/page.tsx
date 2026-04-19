import type { Metadata } from 'next';

import { PageLayout } from '@/components/storefront/cms';
import { AboutPage as AboutPageContent } from '@/components/storefront/cms/About';

export const metadata: Metadata = {
  title: 'About Us',
  description: 'Learn more about LankaCommerce and our mission.',
};

export default function AboutPage() {
  return (
    <PageLayout className="max-w-5xl">
      <AboutPageContent />
    </PageLayout>
  );
}
