'use client';

import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { useEffect, useState } from 'react';

import { Badge } from '@/components/ui/badge';
import { PageLayout } from '@/components/storefront/cms/Layout';
import { getBlogPostBySlug, getBlogPosts } from '@/services/storefront/cmsService';
import type { BlogPost } from '@/types/storefront/cms.types';

import { PostContent } from './PostContent';
import { PostFeaturedImage } from './PostFeaturedImage';
import { PostHeader } from './PostHeader';
import { PostShareButtons } from './PostShareButtons';
import { RelatedPosts } from './RelatedPosts';

interface BlogDetailPageProps {
  slug: string;
}

export function BlogDetailPage({ slug }: BlogDetailPageProps) {
  const [post, setPost] = useState<BlogPost | null>(null);
  const [relatedPosts, setRelatedPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void getBlogPostBySlug(slug).then((p) => {
      setPost(p);
      setLoading(false);
    });
    void getBlogPosts().then((res) => setRelatedPosts(res.data));
  }, [slug]);

  if (loading) {
    return (
      <PageLayout>
        <div className="container mx-auto px-4 py-12 text-center text-muted-foreground">
          Loading post...
        </div>
      </PageLayout>
    );
  }

  if (!post) {
    return (
      <PageLayout>
        <div className="container mx-auto px-4 py-12 text-center">
          <h1 className="text-2xl font-bold">Post not found</h1>
          <Link href="/blog" className="text-primary hover:underline mt-4 inline-block">
            Back to Blog
          </Link>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Breadcrumbs */}
        <nav className="flex items-center gap-1 text-sm text-muted-foreground mb-6">
          <Link href="/" className="hover:text-foreground">Home</Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <Link href="/blog" className="hover:text-foreground">Blog</Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <span className="text-foreground truncate">{post.title}</span>
        </nav>

        <PostHeader post={post} />

        <div className="mt-8">
          <PostFeaturedImage
            src={post.featuredImage ?? ''}
            alt={post.title}
          />
        </div>

        <div className="mt-8">
          <PostContent content={post.content} />
        </div>

        {/* Tags */}
        {post.tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-8">
            {post.tags.map((tag) => (
              <Badge key={tag.id} variant="outline">
                {tag.name}
              </Badge>
            ))}
          </div>
        )}

        <PostShareButtons title={post.title} slug={post.slug} />

        <RelatedPosts posts={relatedPosts} currentSlug={post.slug} />
      </div>
    </PageLayout>
  );
}
