import { cn } from '@/lib/utils';

interface RichContentProps {
  content: string;
  className?: string;
}

export function RichContent({ content, className }: RichContentProps) {
  return (
    <div
      className={cn('prose prose-slate max-w-none dark:prose-invert', className)}
      dangerouslySetInnerHTML={{ __html: content }}
    />
  );
}
