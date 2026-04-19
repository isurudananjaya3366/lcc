import type { ContentBlock } from '@/types/storefront/cms.types';
import { ImageBlock } from './ImageBlock';
import { VideoBlock } from './VideoBlock';
import { QuoteBlock } from './QuoteBlock';
import { ListBlock } from './ListBlock';
import { TableBlock } from './TableBlock';
import { CodeBlock } from './CodeBlock';

interface BlockRendererProps {
  block: ContentBlock;
}

export function BlockRenderer({ block }: BlockRendererProps) {
  switch (block.type) {
    case 'paragraph':
      return <p dangerouslySetInnerHTML={{ __html: block.content }} />;

    case 'heading': {
      const level = (block.metadata?.level as number) ?? 2;
      const Tag = `h${Math.min(Math.max(level, 1), 6)}` as 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
      return <Tag dangerouslySetInnerHTML={{ __html: block.content }} />;
    }

    case 'image':
      return (
        <ImageBlock
          src={block.content}
          alt={(block.metadata?.alt as string) ?? ''}
          caption={block.metadata?.caption as string | undefined}
        />
      );

    case 'video':
      return (
        <VideoBlock
          url={block.content}
          title={block.metadata?.title as string | undefined}
        />
      );

    case 'quote':
      return (
        <QuoteBlock
          quote={block.content}
          author={block.metadata?.author as string | undefined}
        />
      );

    case 'list': {
      const items: string[] = JSON.parse(block.content);
      return (
        <ListBlock
          items={items}
          ordered={block.metadata?.ordered as boolean | undefined}
        />
      );
    }

    case 'table': {
      const { headers, rows } = JSON.parse(block.content) as {
        headers: string[];
        rows: string[][];
      };
      return <TableBlock headers={headers} rows={rows} />;
    }

    case 'code':
      return (
        <CodeBlock
          code={block.content}
          language={block.metadata?.language as string | undefined}
        />
      );

    default:
      return <p dangerouslySetInnerHTML={{ __html: block.content }} />;
  }
}
