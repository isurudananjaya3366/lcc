'use client';

interface ReviewsHeaderProps {
  count: number;
}

export function ReviewsHeader({ count }: ReviewsHeaderProps) {
  return (
    <div className="flex flex-col gap-1">
      <h2 className="text-2xl font-bold tracking-tight">My Reviews</h2>
      <p className="text-sm text-muted-foreground">
        {count === 0
          ? 'No reviews yet'
          : `${count} review${count !== 1 ? 's' : ''} submitted`}
      </p>
    </div>
  );
}
