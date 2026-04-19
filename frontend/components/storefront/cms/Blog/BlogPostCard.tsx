import Link from 'next/link';

import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import type { BlogPost } from '@/types/storefront/cms.types';

import { PostFeaturedImage } from './PostFeaturedImage';
import { PostMeta } from './PostMeta';

interface BlogPostCardProps {
  post: BlogPost;
}

export function BlogPostCard({ post }: BlogPostCardProps) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <Link href={`/blog/${post.slug}`}>
        <PostFeaturedImage
          src={post.featuredImage ?? ''}
          alt={post.title}
        />
      </Link>
      <CardContent className="p-5">
        <Badge variant="secondary" className="mb-2">
          {post.category.name}
        </Badge>
        <h3 className="text-lg font-semibold mb-2 line-clamp-2">
          <Link href={`/blog/${post.slug}`} className="hover:underline">
            {post.title}
          </Link>
        </h3>
        <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
          {post.excerpt}
        </p>
        <PostMeta
          author={post.author}
          date={post.publishedAt ?? post.createdAt}
          readingTime={post.readingTime}
        />
      </CardContent>
    </Card>
  );
}
