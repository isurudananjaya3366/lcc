import { Quote } from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuoteBlockProps {
  quote: string;
  author?: string;
  className?: string;
}

export function QuoteBlock({ quote, author, className }: QuoteBlockProps) {
  return (
    <blockquote
      className={cn(
        'my-6 border-l-4 border-primary/40 pl-6 py-4 bg-muted/50 rounded-r-lg',
        className,
      )}
    >
      <Quote className="h-6 w-6 text-primary/40 mb-2" />
      <p className="text-lg italic leading-relaxed">{quote}</p>
      {author && (
        <footer className="mt-3 text-sm text-muted-foreground">
          — {author}
        </footer>
      )}
    </blockquote>
  );
}
