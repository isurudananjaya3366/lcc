import { cn } from '@/lib/utils';

interface ImageCaptionProps {
  src: string;
  alt: string;
  caption: string;
  className?: string;
}

export function ImageCaption({ src, alt, caption, className }: ImageCaptionProps) {
  return (
    <figure className={cn('my-6', className)}>
      <div
        className="aspect-video bg-muted rounded-lg"
        role="img"
        aria-label={alt}
        style={{ backgroundImage: `url(${src})`, backgroundSize: 'cover', backgroundPosition: 'center' }}
      />
      <figcaption className="text-sm text-center text-muted-foreground mt-2">
        {caption}
      </figcaption>
    </figure>
  );
}
