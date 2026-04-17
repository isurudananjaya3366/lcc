import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { CatalogPage } from '@/components/storefront/catalog';
import { CollectionHero } from '@/components/storefront/catalog/CollectionHero';
import { CollectionDescription } from '@/components/storefront/catalog/CollectionDescription';
import { getCollectionBySlug, getCollectionBreadcrumbs } from '@/lib/store/collections';

type CollectionPageProps = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export async function generateMetadata({ params }: CollectionPageProps): Promise<Metadata> {
  const { slug } = await params;

  if (!slug) {
    return { title: 'Collection Not Found | LankaPOS' };
  }

  const collection = await getCollectionBySlug(slug);

  const title = collection
    ? collection.name
    : slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  const description = collection?.description
    ? collection.description.slice(0, 155)
    : `Explore our ${title} collection. Curated products for you.`;

  return {
    title: `${title} | LankaPOS`,
    description,
    openGraph: {
      title: `${title} | LankaPOS`,
      description,
      ...(collection?.heroImage && { images: [{ url: collection.heroImage }] }),
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: `${title} | LankaPOS`,
      description,
    },
  };
}

export default async function CollectionPage({ params, searchParams }: CollectionPageProps) {
  const { slug } = await params;
  const resolvedSearchParams = await searchParams;

  if (!slug) {
    notFound();
  }

  const collection = await getCollectionBySlug(slug);

  const collectionName = collection
    ? collection.name
    : slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  const breadcrumbs = collection
    ? getCollectionBreadcrumbs(collection)
    : [
        { label: 'Home', href: '/', current: false },
        { label: 'Products', href: '/products', current: false },
        { label: collectionName, current: true },
      ];

  return (
    <div>
      <CollectionHero
        name={collectionName}
        description={collection?.description}
        image={collection?.heroImage}
        productCount={collection?.productCount}
        curatedBy={collection?.curatedBy}
        tags={collection?.tags}
        className="mb-6"
      />
      {collection?.story && (
        <CollectionDescription
          description={collection.description}
          story={collection.story}
          curatorName={collection.curatedBy ?? undefined}
          className="mb-8"
        />
      )}
      <CatalogPage
        title={collectionName}
        breadcrumbs={breadcrumbs}
        collectionSlug={slug}
        searchParams={resolvedSearchParams as Record<string, string | string[]>}
      />
    </div>
  );
}
