import { ImageIcon } from 'lucide-react';

import { cn } from '@/lib/utils';

interface PostFeaturedImageProps {
  src: string;
  alt: string;
  className?: string;
}

export function PostFeaturedImage({ src, alt, className }: PostFeaturedImageProps) {
  void src;
  return (
    <div
      className={cn(
        'aspect-video bg-muted rounded-lg flex items-center justify-center',
        className,
      )}
      aria-label={alt}
    >
      <ImageIcon className="h-12 w-12 text-muted-foreground/40" />
    </div>
  );
}
