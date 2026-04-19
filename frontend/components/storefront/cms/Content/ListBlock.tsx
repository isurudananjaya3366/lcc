import { cn } from '@/lib/utils';

interface ListBlockProps {
  items: string[];
  ordered?: boolean;
  className?: string;
}

export function ListBlock({ items, ordered, className }: ListBlockProps) {
  const Tag = ordered ? 'ol' : 'ul';

  return (
    <Tag
      className={cn(
        'my-6 space-y-2 pl-6',
        ordered ? 'list-decimal' : 'list-disc',
        className,
      )}
    >
      {items.map((item, index) => (
        <li key={index} className="text-muted-foreground">
          {item}
        </li>
      ))}
    </Tag>
  );
}
