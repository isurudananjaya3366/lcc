export type PageStatus = 'draft' | 'published' | 'archived';
export type ContentType = 'page' | 'blog';

export interface PageSEO {
  metaTitle?: string;
  metaDescription?: string;
  metaKeywords?: string[];
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
  canonicalUrl?: string;
  noIndex?: boolean;
}

export interface ContentBlock {
  id: string;
  type: 'paragraph' | 'heading' | 'image' | 'video' | 'quote' | 'list' | 'table' | 'code';
  content: string;
  metadata?: Record<string, unknown>;
}

export interface CMSPage {
  id: string;
  slug: string;
  title: string;
  content: string;
  blocks?: ContentBlock[];
  excerpt?: string;
  featuredImage?: string;
  seo?: PageSEO;
  status: PageStatus;
  template?: string;
  createdAt: string;
  updatedAt: string;
  publishedAt?: string;
}

export interface BlogAuthor {
  id: string;
  name: string;
  avatar?: string;
  bio?: string;
}

export interface BlogCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  postCount?: number;
}

export interface BlogTag {
  id: string;
  name: string;
  slug: string;
}

export interface BlogPost extends CMSPage {
  author: BlogAuthor;
  category: BlogCategory;
  tags: BlogTag[];
  readingTime: number;
}

export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface PagesResponse {
  data: CMSPage[];
  pagination: PaginationMeta;
}

export interface BlogPostsResponse {
  data: BlogPost[];
  pagination: PaginationMeta;
}

export interface FAQItem {
  id: string;
  question: string;
  answer: string;
  category: string;
  order: number;
}

export interface ContactFormData {
  name: string;
  email: string;
  phone?: string;
  subject?: string;
  message: string;
}

export interface PolicySection {
  id: string;
  title: string;
  content: string;
  order: number;
}

export interface ShippingRate {
  id: string;
  zone: string;
  method: string;
  minDays: number;
  maxDays: number;
  price: number;
  freeAbove?: number;
}
