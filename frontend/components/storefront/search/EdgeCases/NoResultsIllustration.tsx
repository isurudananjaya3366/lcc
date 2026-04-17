import { cn } from '@/lib/utils';

interface NoResultsIllustrationProps {
  className?: string;
}

export function NoResultsIllustration({ className }: NoResultsIllustrationProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 200 200"
      fill="none"
      className={cn('h-40 w-40', className)}
      aria-hidden="true"
    >
      {/* Magnifying glass body */}
      <circle
        cx="90"
        cy="85"
        r="50"
        className="stroke-muted-foreground/40"
        strokeWidth="6"
        fill="none"
      />
      {/* Glass fill */}
      <circle
        cx="90"
        cy="85"
        r="47"
        className="fill-muted/30"
      />
      {/* Handle */}
      <line
        x1="127"
        y1="122"
        x2="165"
        y2="160"
        className="stroke-muted-foreground/40"
        strokeWidth="8"
        strokeLinecap="round"
      />
      {/* Question mark */}
      <path
        d="M82 72c0-8 6-14 14-14s14 6 14 14c0 6-4 10-9 12-3 1-5 4-5 7"
        className="stroke-muted-foreground/60"
        strokeWidth="4"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="96" cy="102" r="3" className="fill-muted-foreground/60" />
    </svg>
  );
}
