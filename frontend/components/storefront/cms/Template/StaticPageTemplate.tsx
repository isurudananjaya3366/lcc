import type { CMSPage } from '@/types/storefront/cms.types';
import { PageLayout, PageContentArea } from '@/components/storefront/cms';
import { PageBreadcrumb } from './PageBreadcrumb';
import { PageTitle } from './PageTitle';
import { PageLastUpdated } from './PageLastUpdated';
import { RichContent } from '../Content/RichContent';

interface StaticPageTemplateProps {
  page: CMSPage;
  relatedPages?: { title: string; slug: string; excerpt?: string }[];
}

export function StaticPageTemplate({ page, relatedPages }: StaticPageTemplateProps) {
  return (
    <PageLayout>
      <PageBreadcrumb
        items={[
          { label: 'Home', href: '/' },
          { label: page.title },
        ]}
      />
      <PageTitle title={page.title} description={page.excerpt} />
      <PageContentArea>
        <RichContent content={page.content} />
      </PageContentArea>
      {page.updatedAt && <PageLastUpdated date={page.updatedAt} />}
      {relatedPages && relatedPages.length > 0 && (
        <div className="mt-12">
          {/* Inline related pages to avoid circular barrel imports */}
          <h2 className="text-2xl font-bold tracking-tight mb-4">Related Pages</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {relatedPages.map((rp) => (
              <a
                key={rp.slug}
                href={`/${rp.slug}`}
                className="block rounded-lg border p-4 hover:shadow-md transition-shadow"
              >
                <h3 className="font-semibold">{rp.title}</h3>
                {rp.excerpt && (
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                    {rp.excerpt}
                  </p>
                )}
              </a>
            ))}
          </div>
        </div>
      )}
    </PageLayout>
  );
}
