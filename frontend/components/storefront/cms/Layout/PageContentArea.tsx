import { cn } from '@/lib/utils';

interface PageContentAreaProps {
  children: React.ReactNode;
  className?: string;
}

export function PageContentArea({ children, className }: PageContentAreaProps) {
  return (
    <article className={cn('prose prose-neutral dark:prose-invert max-w-none', className)}>
      {children}
    </article>
  );
}
