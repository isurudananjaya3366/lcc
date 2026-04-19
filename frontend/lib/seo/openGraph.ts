import type { Metadata } from 'next';
import { seoConfig } from './config';
import type { OpenGraphImage } from './types';

export function createOGImage(url: string, alt?: string): OpenGraphImage {
  return { url, width: 1200, height: 630, alt: alt ?? seoConfig.siteName, type: 'image/jpeg' };
}

export function createProductOG(product: {
  name: string;
  description?: string;
  image?: string;
  price: number;
  currency?: string;
  slug: string;
}): NonNullable<Metadata['openGraph']> {
  return {
    title: product.name,
    description: product.description ?? `Buy ${product.name} from ${seoConfig.siteName}`,
    url: `${seoConfig.siteUrl}/products/${product.slug}`,
    siteName: seoConfig.siteName,
    locale: seoConfig.locale,
    type: 'website',
    images: product.image
      ? [createOGImage(product.image, product.name)]
      : [createOGImage(seoConfig.defaultImage)],
  };
}

export function createArticleOG(article: {
  title: string;
  description?: string;
  image?: string;
  author: string;
  publishedAt: string;
  slug: string;
  tags?: string[];
}): NonNullable<Metadata['openGraph']> {
  return {
    title: article.title,
    description: article.description ?? `Read "${article.title}" on ${seoConfig.siteName}`,
    url: `${seoConfig.siteUrl}/blog/${article.slug}`,
    siteName: seoConfig.siteName,
    locale: seoConfig.locale,
    type: 'article',
    publishedTime: article.publishedAt,
    authors: [article.author],
    tags: article.tags,
    images: article.image
      ? [createOGImage(article.image, article.title)]
      : [createOGImage(seoConfig.defaultImage)],
  };
}

export function createDefaultOG(
  title?: string,
  description?: string,
): NonNullable<Metadata['openGraph']> {
  return {
    title: title ?? seoConfig.defaultTitle,
    description: description ?? seoConfig.defaultDescription,
    url: seoConfig.siteUrl,
    siteName: seoConfig.siteName,
    locale: seoConfig.locale,
    type: 'website',
    images: [createOGImage(seoConfig.defaultImage)],
  };
}
