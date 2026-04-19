import type { ContentBlock } from '@/types/storefront/cms.types';
import { cn } from '@/lib/utils';
import { ProseStyles } from './ProseStyles';
import { BlockRenderer } from './BlockRenderer';

interface RichTextRendererProps {
  content: string;
  blocks?: ContentBlock[];
  className?: string;
}

export function RichTextRenderer({ content, blocks, className }: RichTextRendererProps) {
  if (blocks && blocks.length > 0) {
    return (
      <ProseStyles className={className}>
        {blocks.map((block) => (
          <BlockRenderer key={block.id} block={block} />
        ))}
      </ProseStyles>
    );
  }

  return (
    <ProseStyles className={className}>
      <div dangerouslySetInnerHTML={{ __html: content }} />
    </ProseStyles>
  );
}
