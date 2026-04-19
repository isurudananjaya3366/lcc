import { seoConfig } from './config';
import type {
  OrganizationSchema,
  WebSiteSchema,
  ProductSchema,
  BreadcrumbSchema,
  ArticleSchema,
  FAQSchema,
  ContactPageSchema,
  LocalBusinessSchema,
  CollectionPageSchema,
} from './schemas';

export function generateOrganizationSchema(): OrganizationSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: seoConfig.siteName,
    url: seoConfig.siteUrl,
    logo: `${seoConfig.siteUrl}/images/logo.png`,
    description: seoConfig.defaultDescription,
    address: {
      '@type': 'PostalAddress',
      streetAddress: '42 Galle Road',
      addressLocality: 'Colombo 03',
      addressRegion: 'Western Province',
      postalCode: '00300',
      addressCountry: 'LK',
    },
    contactPoint: {
      '@type': 'ContactPoint',
      telephone: '+94-11-234-5678',
      contactType: 'customer service',
      availableLanguage: ['English', 'Sinhala', 'Tamil'],
    },
    sameAs: [
      'https://www.facebook.com/ceylonstore',
      'https://twitter.com/ceylonstore',
      'https://www.instagram.com/ceylonstore',
    ],
  };
}

export function generateWebSiteSchema(): WebSiteSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: seoConfig.siteName,
    url: seoConfig.siteUrl,
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${seoConfig.siteUrl}/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  };
}

export function generateProductSchema(product: {
  name: string;
  description?: string;
  image?: string | string[];
  sku?: string;
  brand?: string;
  price: number;
  currency?: string;
  availability?: 'InStock' | 'OutOfStock' | 'PreOrder';
  slug: string;
  rating?: number;
  reviewCount?: number;
}): ProductSchema {
  const schema: ProductSchema = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.image,
    sku: product.sku,
    ...(product.brand && { brand: { '@type': 'Brand' as const, name: product.brand } }),
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: product.currency ?? 'LKR',
      availability: `https://schema.org/${product.availability ?? 'InStock'}`,
      url: `${seoConfig.siteUrl}/products/${product.slug}`,
      seller: { '@type': 'Organization', name: seoConfig.siteName },
    },
  };
  if (product.rating && product.reviewCount) {
    schema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: product.rating,
      reviewCount: product.reviewCount,
      bestRating: 5,
      worstRating: 1,
    };
  }
  return schema;
}

export function generateBreadcrumbSchema(
  items: { name: string; url?: string }[],
): BreadcrumbSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem' as const,
      position: index + 1,
      name: item.name,
      ...(item.url && { item: `${seoConfig.siteUrl}${item.url}` }),
    })),
  };
}

export function generateArticleSchema(article: {
  title: string;
  description?: string;
  image?: string;
  author: string;
  publishedAt: string;
  updatedAt?: string;
  slug: string;
}): ArticleSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: article.title,
    description: article.description,
    image: article.image,
    author: { '@type': 'Person', name: article.author },
    publisher: {
      '@type': 'Organization',
      name: seoConfig.siteName,
      logo: { '@type': 'ImageObject', url: `${seoConfig.siteUrl}/images/logo.png` },
    },
    datePublished: article.publishedAt,
    dateModified: article.updatedAt ?? article.publishedAt,
    mainEntityOfPage: `${seoConfig.siteUrl}/blog/${article.slug}`,
  };
}

export function generateFAQSchema(
  items: { question: string; answer: string }[],
): FAQSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((item) => ({
      '@type': 'Question' as const,
      name: item.question,
      acceptedAnswer: { '@type': 'Answer' as const, text: item.answer },
    })),
  };
}

export function generateContactPageSchema(): ContactPageSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'ContactPage',
    name: 'Contact Us',
    url: `${seoConfig.siteUrl}/contact`,
    description: `Contact ${seoConfig.siteName} for inquiries about Sri Lankan products.`,
  };
}

export function generateLocalBusinessSchema(): LocalBusinessSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'LocalBusiness',
    name: seoConfig.siteName,
    url: seoConfig.siteUrl,
    telephone: '+94-11-234-5678',
    email: 'info@store.lk',
    address: {
      '@type': 'PostalAddress',
      streetAddress: '42 Galle Road',
      addressLocality: 'Colombo 03',
      addressRegion: 'Western Province',
      postalCode: '00300',
      addressCountry: 'LK',
    },
    openingHours: 'Mo-Sa 09:00-18:00',
    geo: { '@type': 'GeoCoordinates', latitude: 6.9271, longitude: 79.8612 },
    priceRange: '₨₨',
  };
}

export function generateCollectionPageSchema(collection: {
  name: string;
  slug: string;
  description?: string;
}): CollectionPageSchema {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: collection.name,
    url: `${seoConfig.siteUrl}/collections/${collection.slug}`,
    description: collection.description,
  };
}
