import { cn } from '@/lib/utils';

interface CatalogTitleProps {
  title: string;
  as?: 'h1' | 'h2';
  className?: string;
}

export function CatalogTitle({ title, as: Tag = 'h1', className }: CatalogTitleProps) {
  return (
    <Tag
      className={cn(
        'text-2xl font-bold leading-tight text-gray-900 md:text-3xl lg:text-4xl',
        className
      )}
    >
      {title}
    </Tag>
  );
}
