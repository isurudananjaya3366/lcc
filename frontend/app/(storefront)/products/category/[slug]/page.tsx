import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { CatalogPage } from '@/components/storefront/catalog';
import { CategoryHero } from '@/components/storefront/catalog/CategoryHero';
import { SubcategoryGrid } from '@/components/storefront/catalog/SubcategoryGrid';
import {
  getCategoryBySlug,
  getSubcategories,
  getCategoryBreadcrumbs,
} from '@/lib/store/categories';

type CategoryPageProps = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export async function generateMetadata({ params }: CategoryPageProps): Promise<Metadata> {
  const { slug } = await params;

  if (!slug) {
    return { title: 'Category Not Found | LankaPOS' };
  }

  const category = await getCategoryBySlug(slug);

  const title = category
    ? category.name
    : slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  const description = category?.description
    ? category.description.slice(0, 155)
    : `Browse ${title} products. Find quality items at great prices.`;

  return {
    title: `${title} | LankaPOS`,
    description,
    openGraph: {
      title: `${title} | LankaPOS`,
      description,
      ...(category?.image && { images: [{ url: category.image }] }),
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title: `${title} | LankaPOS`,
      description,
    },
  };
}

export default async function CategoryPage({ params, searchParams }: CategoryPageProps) {
  const { slug } = await params;
  const resolvedSearchParams = await searchParams;

  if (!slug) {
    notFound();
  }

  const category = await getCategoryBySlug(slug);

  const categoryName = category
    ? category.name
    : slug.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  const subcategories = category ? await getSubcategories(category.id) : [];

  const breadcrumbs = category
    ? getCategoryBreadcrumbs(category)
    : [
        { label: 'Home', href: '/', current: false },
        { label: 'Products', href: '/products', current: false },
        { label: categoryName, current: true },
      ];

  return (
    <div>
      <CategoryHero
        name={categoryName}
        description={category?.description}
        image={category?.image}
        productCount={category?.productCount}
        className="mb-6"
      />
      {subcategories.length > 0 && <SubcategoryGrid categories={subcategories} className="mb-8" />}
      <CatalogPage
        title={categoryName}
        breadcrumbs={breadcrumbs}
        categorySlug={slug}
        searchParams={resolvedSearchParams as Record<string, string | string[]>}
      />
    </div>
  );
}
