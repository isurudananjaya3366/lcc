import type { Metadata } from 'next';
import { seoConfig } from './config';

export function createTwitterCard(params: {
  title?: string;
  description?: string;
  image?: string;
  cardType?: 'summary' | 'summary_large_image';
}): NonNullable<Metadata['twitter']> {
  return {
    card: params.cardType ?? 'summary_large_image',
    title: params.title ?? seoConfig.defaultTitle,
    description: params.description ?? seoConfig.defaultDescription,
    images: params.image ? [params.image] : [seoConfig.defaultImage],
    creator: seoConfig.twitterHandle,
    site: seoConfig.twitterHandle,
  };
}

export function createProductTwitterCard(product: {
  name: string;
  description?: string;
  image?: string;
}): NonNullable<Metadata['twitter']> {
  return createTwitterCard({
    title: product.name,
    description: product.description,
    image: product.image,
    cardType: 'summary_large_image',
  });
}

export function createArticleTwitterCard(article: {
  title: string;
  description?: string;
  image?: string;
}): NonNullable<Metadata['twitter']> {
  return createTwitterCard({
    title: article.title,
    description: article.description,
    image: article.image,
    cardType: 'summary_large_image',
  });
}
