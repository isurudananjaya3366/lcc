import type { Metadata } from 'next';

import { BlogListPage } from '@/components/storefront/cms/Blog';

export const metadata: Metadata = {
  title: 'Blog',
  description: 'Latest news, tips, and updates from LankaCommerce.',
};

export default function BlogPage() {
  return <BlogListPage />;
}
