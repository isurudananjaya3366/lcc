import type { BlogPost } from '@/types/storefront/cms.types';

import { BlogPostCard } from './BlogPostCard';

interface RelatedPostsProps {
  posts: BlogPost[];
  currentSlug: string;
}

export function RelatedPosts({ posts, currentSlug }: RelatedPostsProps) {
  const related = posts
    .filter((p) => p.slug !== currentSlug)
    .slice(0, 3);

  if (related.length === 0) return null;

  return (
    <section className="mt-12">
      <h2 className="text-2xl font-bold mb-6">Related Posts</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {related.map((post) => (
          <BlogPostCard key={post.id} post={post} />
        ))}
      </div>
    </section>
  );
}
