import type { Metadata } from 'next';

/** Props for generating store page metadata */
export interface StoreHeadProps {
  title?: string;
  description?: string;
  image?: string;
  type?: 'website' | 'article';
  keywords?: string[];
  noindex?: boolean;
  canonical?: string;
}

/** Default metadata constants */
const SITE_NAME = 'LankaCommerce Cloud';
const DEFAULT_TITLE = `${SITE_NAME} | Sri Lankan E-Commerce Platform`;
const DEFAULT_DESCRIPTION =
  'Shop quality products from Sri Lanka. Electronics, fashion, home & garden, and more with secure checkout and fast delivery island-wide.';
const DEFAULT_IMAGE = '/images/og-default.jpg';
const DEFAULT_LOCALE = 'en_LK';

/**
 * Generate metadata for a storefront page.
 * Merges provided props with default values.
 */
export function generateStoreMetadata(props: StoreHeadProps = {}): Metadata {
  const {
    title,
    description = DEFAULT_DESCRIPTION,
    image = DEFAULT_IMAGE,
    type = 'website',
    keywords = [],
    noindex = false,
  } = props;

  const pageTitle = title ? `${title} | ${SITE_NAME}` : DEFAULT_TITLE;

  return {
    title: pageTitle,
    description,
    keywords: keywords.length > 0 ? keywords : undefined,
    robots: noindex ? { index: false, follow: false } : { index: true, follow: true },
    openGraph: {
      title: pageTitle,
      description,
      siteName: SITE_NAME,
      locale: DEFAULT_LOCALE,
      type,
      images: [{ url: image, width: 1200, height: 630, alt: pageTitle }],
    },
    twitter: {
      card: 'summary_large_image',
      title: pageTitle,
      description,
      images: [image],
    },
  };
}

/** Generate metadata for a product page */
export function productMetadata(product: {
  name: string;
  description: string;
  image?: string;
  price?: number;
  currency?: string;
}): Metadata {
  return generateStoreMetadata({
    title: product.name,
    description: product.description,
    image: product.image,
    type: 'website',
    keywords: [product.name, 'buy online', 'Sri Lanka'],
  });
}

/** Generate metadata for a category page */
export function categoryMetadata(category: {
  name: string;
  description?: string;
  image?: string;
}): Metadata {
  return generateStoreMetadata({
    title: category.name,
    description: category.description ?? `Browse ${category.name} products at LankaCommerce Cloud`,
    image: category.image,
  });
}

/** Generate metadata for a static page */
export function pageMetadata(page: { title: string; description: string }): Metadata {
  return generateStoreMetadata({
    title: page.title,
    description: page.description,
  });
}

export default generateStoreMetadata;
