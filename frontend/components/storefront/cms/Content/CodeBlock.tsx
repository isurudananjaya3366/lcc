import { cn } from '@/lib/utils';

interface CodeBlockProps {
  code: string;
  language?: string;
  className?: string;
}

export function CodeBlock({ code, language, className }: CodeBlockProps) {
  return (
    <div className={cn('relative my-6', className)}>
      {language && (
        <div className="absolute top-0 right-0 px-3 py-1 text-xs text-muted-foreground bg-muted border-b border-l rounded-bl-lg rounded-tr-lg font-mono">
          {language}
        </div>
      )}
      <pre className="bg-muted border rounded-lg p-4 overflow-x-auto">
        <code className="text-sm font-mono">{code}</code>
      </pre>
    </div>
  );
}
