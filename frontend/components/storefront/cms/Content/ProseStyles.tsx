import { cn } from '@/lib/utils';

interface ProseStylesProps {
  children: React.ReactNode;
  className?: string;
}

export function ProseStyles({ children, className }: ProseStylesProps) {
  return (
    <div
      className={cn(
        'prose prose-slate max-w-none dark:prose-invert',
        'prose-headings:font-semibold prose-headings:tracking-tight',
        'prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl',
        'prose-p:leading-7 prose-p:text-muted-foreground',
        'prose-a:text-primary prose-a:underline prose-a:underline-offset-4 hover:prose-a:text-primary/80',
        'prose-blockquote:border-l-primary prose-blockquote:text-muted-foreground',
        'prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono',
        'prose-pre:bg-muted prose-pre:border prose-pre:rounded-lg',
        'prose-img:rounded-lg',
        'prose-table:border prose-th:bg-muted prose-th:p-3 prose-td:p-3',
        'prose-li:text-muted-foreground',
        className,
      )}
    >
      {children}
    </div>
  );
}
