import Image from 'next/image';
import { cn } from '@/lib/utils';

interface ImageBlockProps {
  src: string;
  alt: string;
  caption?: string;
  className?: string;
}

export function ImageBlock({ src, alt, caption, className }: ImageBlockProps) {
  return (
    <figure className={cn('my-6', className)}>
      <Image
        src={src}
        alt={alt}
        width={800}
        height={450}
        className="rounded-lg w-full h-auto"
      />
      {caption && (
        <figcaption className="mt-2 text-center text-sm text-muted-foreground">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
