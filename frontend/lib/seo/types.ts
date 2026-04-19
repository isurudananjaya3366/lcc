export interface SEOConfig {
  siteName: string;
  siteUrl: string;
  defaultTitle: string;
  titleTemplate: string;
  defaultDescription: string;
  defaultImage: string;
  twitterHandle?: string;
  facebookAppId?: string;
  locale: string;
  themeColor: string;
}

export interface PageSEO {
  title?: string;
  description?: string;
  image?: string;
  url?: string;
  noIndex?: boolean;
  keywords?: string[];
}

export interface OpenGraphImage {
  url: string;
  width?: number;
  height?: number;
  alt?: string;
  type?: string;
}

export interface ProductSEO {
  name: string;
  description: string;
  price: number;
  currency: string;
  image?: string;
  sku?: string;
  brand?: string;
  availability?: 'InStock' | 'OutOfStock' | 'PreOrder';
  slug: string;
}

export interface BlogSEO {
  title: string;
  description: string;
  image?: string;
  author: string;
  publishedAt: string;
  updatedAt?: string;
  category?: string;
  tags?: string[];
  slug: string;
}

export interface CategorySEO {
  name: string;
  description?: string;
  slug: string;
  image?: string;
}
