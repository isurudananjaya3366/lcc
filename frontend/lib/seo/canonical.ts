import { seoConfig } from './config';

export function getCanonicalUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  // Remove trailing slash except for root
  const normalizedPath = cleanPath === '/' ? '' : cleanPath.replace(/\/$/, '');
  return `${seoConfig.siteUrl}${normalizedPath}`;
}

export function getHomepageCanonical(): string {
  return seoConfig.siteUrl;
}

export function getProductCanonical(slug: string): string {
  return getCanonicalUrl(`/products/${slug}`);
}

export function getCategoryCanonical(slug: string): string {
  // Strip query params for category — canonical is the base category URL
  return getCanonicalUrl(`/products?category=${slug}`);
}

export function getBlogCanonical(slug: string): string {
  return getCanonicalUrl(`/blog/${slug}`);
}

export function getPaginationCanonical(basePath: string, page: number): string {
  // Page 1 canonical is the base path (no ?page=1)
  if (page <= 1) return getCanonicalUrl(basePath);
  return getCanonicalUrl(`${basePath}?page=${page}`);
}

export function getFilterCanonical(basePath: string): string {
  // Filtered pages point to base path as canonical to avoid duplicate content
  return getCanonicalUrl(basePath);
}

// For future multi-language support
export interface AlternateLink {
  hrefLang: string;
  href: string;
}

export function getAlternateLinks(path: string): AlternateLink[] {
  // Currently single-language, prepared for future i18n
  return [
    { hrefLang: 'en', href: getCanonicalUrl(path) },
    { hrefLang: 'x-default', href: getCanonicalUrl(path) },
  ];
}
