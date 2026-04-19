export type {
  SEOConfig,
  PageSEO,
  OpenGraphImage,
  ProductSEO,
  BlogSEO,
  CategorySEO,
} from './types';

export { seoConfig } from './config';
export { baseMetadata } from './base';
export {
  constructMetadata,
  generateHomepageMetadata,
  generateProductMetadata,
  generateCategoryMetadata,
  generateCollectionMetadata,
  generateSearchMetadata,
  generateBlogMetadata,
  generateCMSPageMetadata,
} from './metadata';
export type { ConstructMetadataParams } from './metadata';

// Open Graph helpers
export {
  createOGImage,
  createProductOG,
  createArticleOG,
  createDefaultOG,
} from './openGraph';

// Twitter Card helpers
export {
  createTwitterCard,
  createProductTwitterCard,
  createArticleTwitterCard,
} from './twitterCard';

// JSON-LD schema types
export type {
  JsonLdBase,
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

// JSON-LD generators
export {
  generateOrganizationSchema,
  generateWebSiteSchema,
  generateProductSchema,
  generateBreadcrumbSchema,
  generateArticleSchema,
  generateFAQSchema,
  generateContactPageSchema,
  generateLocalBusinessSchema,
  generateCollectionPageSchema,
} from './jsonLd';

// Canonical URL helpers
export type { AlternateLink } from './canonical';
export {
  getCanonicalUrl,
  getHomepageCanonical,
  getProductCanonical,
  getCategoryCanonical,
  getBlogCanonical,
  getPaginationCanonical,
  getFilterCanonical,
  getAlternateLinks,
} from './canonical';
