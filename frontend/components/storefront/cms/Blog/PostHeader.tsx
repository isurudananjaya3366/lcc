import { Badge } from '@/components/ui/badge';
import type { BlogPost } from '@/types/storefront/cms.types';

import { PostMeta } from './PostMeta';

interface PostHeaderProps {
  post: BlogPost;
}

export function PostHeader({ post }: PostHeaderProps) {
  return (
    <div className="space-y-4">
      <Badge variant="secondary">{post.category.name}</Badge>
      <h1 className="text-3xl md:text-4xl font-bold tracking-tight">
        {post.title}
      </h1>
      <PostMeta
        author={post.author}
        date={post.publishedAt ?? post.createdAt}
        readingTime={post.readingTime}
      />
    </div>
  );
}
