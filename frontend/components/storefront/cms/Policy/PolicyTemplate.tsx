import Link from 'next/link';
import type { PolicySection } from '@/types/storefront/cms.types';
import { PageLayout, PageHeader } from '@/components/storefront/cms/Layout';
import { RichContent } from '@/components/storefront/cms/Content';
import { AnchorHeading } from './AnchorHeading';
import { TableOfContents } from './TableOfContents';

interface PolicyTemplateProps {
  title: string;
  sections: PolicySection[];
  updatedAt?: string;
  relatedPolicies?: { title: string; slug: string }[];
}

export function PolicyTemplate({
  title,
  sections,
  updatedAt,
  relatedPolicies,
}: PolicyTemplateProps) {
  const tocItems = sections.map((s) => ({ id: s.id, title: s.title }));

  return (
    <PageLayout className="max-w-6xl">
      <PageHeader
        title={title}
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: title },
        ]}
      />

      {updatedAt && (
        <p className="text-sm text-muted-foreground -mt-4 mb-8">
          Last updated: {updatedAt}
        </p>
      )}

      <div className="lg:grid lg:grid-cols-[1fr_250px] lg:gap-10">
        <main className="space-y-8">
          {sections
            .sort((a, b) => a.order - b.order)
            .map((section) => (
              <section key={section.id} className="space-y-3">
                <AnchorHeading id={section.id} title={section.title} />
                <RichContent content={section.content} />
              </section>
            ))}

          {relatedPolicies && relatedPolicies.length > 0 && (
            <div className="border-t pt-8 mt-12">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
                Related Policies
              </h3>
              <ul className="flex flex-wrap gap-3">
                {relatedPolicies.map((p) => (
                  <li key={p.slug}>
                    <Link
                      href={`/${p.slug}`}
                      className="text-sm text-primary hover:underline"
                    >
                      {p.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </main>

        <aside className="hidden lg:block">
          <TableOfContents sections={tocItems} />
        </aside>
      </div>
    </PageLayout>
  );
}
