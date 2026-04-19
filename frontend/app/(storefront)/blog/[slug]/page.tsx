import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

import { BlogDetailPage } from '@/components/storefront/cms/Blog';
import { getBlogPostBySlug } from '@/services/storefront/cmsService';

interface BlogPostPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: BlogPostPageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getBlogPostBySlug(slug);

  if (!post) {
    return { title: 'Post Not Found' };
  }

  return {
    title: post.seo?.metaTitle ?? post.title,
    description: post.seo?.metaDescription ?? post.excerpt,
    openGraph: {
      title: post.seo?.ogTitle ?? post.title,
      description: post.seo?.ogDescription ?? post.excerpt,
      images: post.seo?.ogImage ? [post.seo.ogImage] : undefined,
    },
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const { slug } = await params;
  const post = await getBlogPostBySlug(slug);

  if (!post) {
    notFound();
  }

  return <BlogDetailPage slug={slug} />;
}
