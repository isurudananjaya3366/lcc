import { Hash } from 'lucide-react';

interface AnchorHeadingProps {
  id: string;
  title: string;
}

export function AnchorHeading({ id, title }: AnchorHeadingProps) {
  return (
    <h2
      id={id}
      className="scroll-mt-20 text-xl font-semibold tracking-tight group flex items-center gap-2"
    >
      {title}
      <a
        href={`#${id}`}
        className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground"
        aria-label={`Link to ${title}`}
      >
        <Hash className="h-4 w-4" />
      </a>
    </h2>
  );
}
