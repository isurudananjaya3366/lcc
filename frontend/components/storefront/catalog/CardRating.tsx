import { cn } from '@/lib/utils';

interface CardRatingProps {
  rating: number;
  reviewCount: number;
  className?: string;
}

function StarIcon({ type }: { type: 'full' | 'half' | 'empty' }) {
  if (type === 'full') {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        className="text-yellow-400 fill-current"
      >
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    );
  }

  if (type === 'half') {
    return (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        className="text-yellow-400"
      >
        <defs>
          <linearGradient id="half-star">
            <stop offset="50%" stopColor="currentColor" />
            <stop offset="50%" stopColor="#D1D5DB" />
          </linearGradient>
        </defs>
        <polygon
          points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
          fill="url(#half-star)"
        />
      </svg>
    );
  }

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      className="text-gray-300 fill-current"
    >
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  );
}

function formatReviewCount(count: number): string {
  if (count >= 1000) {
    return `(${(count / 1000).toFixed(1)}K)`;
  }
  return `(${count})`;
}

export function CardRating({ rating, reviewCount, className }: CardRatingProps) {
  if (reviewCount === 0) return null;

  const stars = Array.from({ length: 5 }, (_, i) => {
    const diff = rating - i;
    if (diff >= 1) return 'full' as const;
    if (diff >= 0.5) return 'half' as const;
    return 'empty' as const;
  });

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {stars.map((type, i) => (
        <StarIcon key={i} type={type} />
      ))}
      <span className="text-xs text-gray-600">{rating.toFixed(1)}</span>
      <span className="text-xs text-gray-400">{formatReviewCount(reviewCount)}</span>
    </div>
  );
}
