import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import Script from 'next/script';
import { getProductBySlug, getRelatedProductsBySlug, getProductBreadcrumbs } from '@/lib/store/products';
import { ProductDetailContainer } from '@/components/storefront/product';
import type { BreadcrumbItem } from '@/components/storefront/catalog/Breadcrumb';

type ProductPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateMetadata({ params }: ProductPageProps): Promise<Metadata> {
  const { slug } = await params;
  const product = await getProductBySlug(slug);

  if (!product) {
    return { title: 'Product Not Found | LankaPOS' };
  }

  const primaryImage = product.images?.find((img) => img.is_primary) ?? product.images?.[0];

  return {
    title: `${product.name} | LankaPOS`,
    description: product.description?.slice(0, 160) || `Buy ${product.name} at the best price.`,
    openGraph: {
      title: product.name,
      description: product.description?.slice(0, 160),
      images: primaryImage ? [{ url: primaryImage.url, alt: primaryImage.alt_text }] : undefined,
    },
  };
}

export async function generateStaticParams() {
  // ISR – start with no pre-rendered pages; paths will be generated on-demand
  return [];
}

export const revalidate = 3600;

function buildBreadcrumbJsonLd(breadcrumbs: BreadcrumbItem[]) {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://lankacommerce.lk';
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.label,
      item: item.href ? `${baseUrl}${item.href}` : undefined,
    })),
  };
}

export default async function ProductDetailPage({ params }: ProductPageProps) {
  const { slug } = await params;

  const [product, relatedProducts] = await Promise.all([
    getProductBySlug(slug),
    getRelatedProductsBySlug(slug, 4),
  ]);

  if (!product) {
    notFound();
  }

  const breadcrumbs = getProductBreadcrumbs(product);
  const breadcrumbJsonLd = buildBreadcrumbJsonLd(breadcrumbs);

  return (
    <>
      <Script
        id="breadcrumb-jsonld"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <ProductDetailContainer
        product={product}
        breadcrumbs={breadcrumbs}
        relatedProducts={relatedProducts}
      />
    </>
  );
}
