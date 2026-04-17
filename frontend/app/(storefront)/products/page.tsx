import type { Metadata } from 'next';
import { CatalogPage } from '@/components/storefront/catalog';

export const metadata: Metadata = {
  title: 'All Products | LankaPOS',
  description: 'Browse our full catalog of quality products. Filter by category, price, and more.',
};

type ProductsPageProps = {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
};

export default async function ProductsPage({ searchParams }: ProductsPageProps) {
  const resolvedSearchParams = await searchParams;

  const breadcrumbs = [
    { label: 'Home', href: '/', current: false },
    { label: 'All Products', current: true },
  ];

  return (
    <CatalogPage
      title="All Products"
      breadcrumbs={breadcrumbs}
      searchParams={resolvedSearchParams as Record<string, string | string[]>}
    />
  );
}
