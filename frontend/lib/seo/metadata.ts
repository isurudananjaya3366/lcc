import type { Metadata } from 'next';
import { seoConfig } from './config';

function truncateDescription(desc: string, maxLength = 160): string {
  if (desc.length <= maxLength) return desc;
  return desc.substring(0, maxLength - 3).trimEnd() + '...';
}

function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '').trim();
}

function formatTitle(title?: string): string {
  if (!title) return seoConfig.defaultTitle;
  return title;
}

export interface ConstructMetadataParams {
  title?: string;
  description?: string;
  image?: string;
  url?: string;
  noIndex?: boolean;
  keywords?: string[];
  type?: 'website' | 'article' | 'product';
  publishedTime?: string;
  modifiedTime?: string;
  authors?: string[];
}

export function constructMetadata(params: ConstructMetadataParams = {}): Metadata {
  const {
    title,
    description,
    image,
    url,
    noIndex = false,
    keywords = [],
    type = 'website',
    publishedTime,
    modifiedTime,
    authors,
  } = params;

  const cleanDescription = description
    ? truncateDescription(stripHtml(description))
    : seoConfig.defaultDescription;
  const ogImage = image ?? seoConfig.defaultImage;
  const pageUrl = url ? `${seoConfig.siteUrl}${url}` : seoConfig.siteUrl;

  const metadata: Metadata = {
    title: formatTitle(title),
    description: cleanDescription,
    keywords: [...seoConfig.defaultDescription.split(' ').slice(0, 3), ...keywords],
    openGraph: {
      title: title ?? seoConfig.defaultTitle,
      description: cleanDescription,
      url: pageUrl,
      siteName: seoConfig.siteName,
      locale: seoConfig.locale,
      type: type === 'article' ? 'article' : 'website',
      images: [{ url: ogImage, width: 1200, height: 630, alt: title ?? seoConfig.siteName }],
      ...(publishedTime && { publishedTime }),
      ...(modifiedTime && { modifiedTime }),
      ...(authors && { authors }),
    },
    twitter: {
      card: 'summary_large_image',
      title: title ?? seoConfig.defaultTitle,
      description: cleanDescription,
      images: [ogImage],
      creator: seoConfig.twitterHandle,
    },
    alternates: {
      canonical: pageUrl,
    },
    ...(noIndex && {
      robots: {
        index: false,
        follow: false,
        googleBot: { index: false, follow: false },
      },
    }),
  };

  return metadata;
}

// Page-specific metadata generators
export function generateHomepageMetadata(): Metadata {
  return constructMetadata({
    title: undefined, // Uses default
    description: seoConfig.defaultDescription,
    url: '/',
  });
}

export function generateProductMetadata(product: {
  name: string;
  description?: string;
  image?: string;
  slug: string;
  price?: number;
  currency?: string;
}): Metadata {
  return constructMetadata({
    title: product.name,
    description:
      product.description ?? `Buy ${product.name} from Ceylon Store. Authentic Sri Lankan product.`,
    image: product.image,
    url: `/products/${product.slug}`,
    type: 'product',
    keywords: [product.name.toLowerCase()],
  });
}

export function generateCategoryMetadata(category: {
  name: string;
  description?: string;
  slug: string;
}): Metadata {
  return constructMetadata({
    title: category.name,
    description:
      category.description ??
      `Browse ${category.name} - authentic Sri Lankan products at Ceylon Store.`,
    url: `/products?category=${category.slug}`,
  });
}

export function generateCollectionMetadata(collection: {
  name: string;
  description?: string;
  slug: string;
}): Metadata {
  return constructMetadata({
    title: collection.name,
    description:
      collection.description ??
      `Explore our ${collection.name} collection at Ceylon Store.`,
    url: `/collections/${collection.slug}`,
  });
}

export function generateSearchMetadata(query?: string): Metadata {
  return constructMetadata({
    title: query ? `Search: ${query}` : 'Search Products',
    description: query
      ? `Search results for "${query}" at Ceylon Store.`
      : 'Search our collection of authentic Sri Lankan products.',
    url: query ? `/search?q=${encodeURIComponent(query)}` : '/search',
    noIndex: true,
  });
}

export function generateBlogMetadata(post: {
  title: string;
  excerpt?: string;
  featuredImage?: string;
  slug: string;
  publishedAt?: string;
  updatedAt?: string;
  author?: string;
}): Metadata {
  return constructMetadata({
    title: post.title,
    description: post.excerpt ?? `Read "${post.title}" on the Ceylon Store blog.`,
    image: post.featuredImage,
    url: `/blog/${post.slug}`,
    type: 'article',
    publishedTime: post.publishedAt,
    modifiedTime: post.updatedAt,
    authors: post.author ? [post.author] : undefined,
  });
}

export function generateCMSPageMetadata(page: {
  title: string;
  seo?: { metaDescription?: string; metaTitle?: string; ogImage?: string; noIndex?: boolean };
  slug: string;
}): Metadata {
  return constructMetadata({
    title: page.seo?.metaTitle ?? page.title,
    description: page.seo?.metaDescription,
    image: page.seo?.ogImage,
    url: `/${page.slug}`,
    noIndex: page.seo?.noIndex,
  });
}
