import { User, Calendar, Clock } from 'lucide-react';

import type { BlogAuthor } from '@/types/storefront/cms.types';

interface PostMetaProps {
  author: BlogAuthor;
  date: string;
  readingTime: number;
}

export function PostMeta({ author, date, readingTime }: PostMetaProps) {
  const formattedDate = new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
      <div className="flex items-center gap-1.5">
        <div className="h-6 w-6 rounded-full bg-muted flex items-center justify-center">
          <User className="h-3.5 w-3.5" />
        </div>
        <span>{author.name}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <Calendar className="h-4 w-4" />
        <span>{formattedDate}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <Clock className="h-4 w-4" />
        <span>{readingTime} min read</span>
      </div>
    </div>
  );
}
