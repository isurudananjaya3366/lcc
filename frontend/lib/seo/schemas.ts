export interface JsonLdBase {
  '@context': 'https://schema.org';
  '@type': string;
}

export interface OrganizationSchema extends JsonLdBase {
  '@type': 'Organization';
  name: string;
  url: string;
  logo?: string;
  description?: string;
  address?: {
    '@type': 'PostalAddress';
    streetAddress: string;
    addressLocality: string;
    addressRegion: string;
    postalCode: string;
    addressCountry: string;
  };
  contactPoint?: {
    '@type': 'ContactPoint';
    telephone: string;
    contactType: string;
    availableLanguage: string[];
  };
  sameAs?: string[];
}

export interface WebSiteSchema extends JsonLdBase {
  '@type': 'WebSite';
  name: string;
  url: string;
  potentialAction?: {
    '@type': 'SearchAction';
    target: { '@type': 'EntryPoint'; urlTemplate: string };
    'query-input': string;
  };
}

export interface ProductSchema extends JsonLdBase {
  '@type': 'Product';
  name: string;
  description?: string;
  image?: string | string[];
  sku?: string;
  brand?: { '@type': 'Brand'; name: string };
  offers: {
    '@type': 'Offer';
    price: number;
    priceCurrency: string;
    availability: string;
    url: string;
    seller?: { '@type': 'Organization'; name: string };
  };
  aggregateRating?: {
    '@type': 'AggregateRating';
    ratingValue: number;
    reviewCount: number;
    bestRating?: number;
    worstRating?: number;
  };
}

export interface BreadcrumbSchema extends JsonLdBase {
  '@type': 'BreadcrumbList';
  itemListElement: {
    '@type': 'ListItem';
    position: number;
    name: string;
    item?: string;
  }[];
}

export interface ArticleSchema extends JsonLdBase {
  '@type': 'Article' | 'BlogPosting';
  headline: string;
  description?: string;
  image?: string;
  author: { '@type': 'Person'; name: string };
  publisher: {
    '@type': 'Organization';
    name: string;
    logo?: { '@type': 'ImageObject'; url: string };
  };
  datePublished: string;
  dateModified?: string;
  mainEntityOfPage?: string;
}

export interface FAQSchema extends JsonLdBase {
  '@type': 'FAQPage';
  mainEntity: {
    '@type': 'Question';
    name: string;
    acceptedAnswer: { '@type': 'Answer'; text: string };
  }[];
}

export interface ContactPageSchema extends JsonLdBase {
  '@type': 'ContactPage';
  name: string;
  url: string;
  description?: string;
}

export interface LocalBusinessSchema extends JsonLdBase {
  '@type': 'LocalBusiness';
  name: string;
  url: string;
  telephone: string;
  email?: string;
  address: {
    '@type': 'PostalAddress';
    streetAddress: string;
    addressLocality: string;
    addressRegion: string;
    postalCode: string;
    addressCountry: string;
  };
  openingHours: string;
  geo?: { '@type': 'GeoCoordinates'; latitude: number; longitude: number };
  priceRange?: string;
}

export interface CollectionPageSchema extends JsonLdBase {
  '@type': 'CollectionPage';
  name: string;
  url: string;
  description?: string;
}
