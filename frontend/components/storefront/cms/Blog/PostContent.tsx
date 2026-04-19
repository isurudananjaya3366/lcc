import { RichContent } from '@/components/storefront/cms/Content';

interface PostContentProps {
  content: string;
}

export function PostContent({ content }: PostContentProps) {
  return (
    <div className="prose prose-lg max-w-none dark:prose-invert">
      <RichContent content={content} />
    </div>
  );
}
