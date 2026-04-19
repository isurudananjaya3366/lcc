import { cn } from '@/lib/utils';

interface VideoBlockProps {
  url: string;
  title?: string;
  className?: string;
}

export function VideoBlock({ url, title, className }: VideoBlockProps) {
  return (
    <div className={cn('my-6', className)}>
      <div className="aspect-video rounded-lg overflow-hidden">
        <iframe
          src={url}
          title={title ?? 'Embedded video'}
          className="w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    </div>
  );
}
