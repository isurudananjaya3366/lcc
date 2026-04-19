import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

import { PageLayout, PageHeader, PageContentArea } from '@/components/storefront/cms';
import { getPageBySlug } from '@/services/storefront/cmsService';

interface CMSPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: CMSPageProps): Promise<Metadata> {
  const { slug } = await params;
  const page = await getPageBySlug(slug);

  if (!page) {
    return { title: 'Page Not Found' };
  }

  return {
    title: page.seo?.metaTitle ?? page.title,
    description: page.seo?.metaDescription ?? page.excerpt,
    openGraph: {
      title: page.seo?.ogTitle ?? page.title,
      description: page.seo?.ogDescription ?? page.excerpt,
      images: page.seo?.ogImage ? [page.seo.ogImage] : undefined,
    },
  };
}

export default async function CMSSlugPage({ params }: CMSPageProps) {
  const { slug } = await params;
  const page = await getPageBySlug(slug);

  if (!page) {
    notFound();
  }

  return (
    <PageLayout>
      <PageHeader
        title={page.title}
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: page.title },
        ]}
      />
      <PageContentArea>
        <div dangerouslySetInnerHTML={{ __html: page.content }} />
      </PageContentArea>
    </PageLayout>
  );
}
