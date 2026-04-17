import { cn } from '@/lib/utils';

interface NoResultsSuggestionsProps {
  className?: string;
}

const SUGGESTIONS = [
  'Check your spelling',
  'Use fewer keywords',
  'Try different keywords',
  'Browse categories instead',
];

export function NoResultsSuggestions({ className }: NoResultsSuggestionsProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-border bg-muted/50 p-4 dark:bg-muted/20',
        className,
      )}
    >
      <h3 className="mb-2 text-sm font-semibold text-foreground">
        Try these suggestions:
      </h3>
      <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
        {SUGGESTIONS.map((suggestion) => (
          <li key={suggestion}>{suggestion}</li>
        ))}
      </ul>
    </div>
  );
}
