import { StarRating } from './StarRating';

interface ReviewCardProps {
  userName: string;
  rating: number;
  title: string;
  content: string;
  createdAt: string;
  isVerified: boolean;
}

export function ReviewCard({
  userName,
  rating,
  title,
  content,
  createdAt,
  isVerified,
}: ReviewCardProps) {
  const formattedDate = new Date(createdAt).toLocaleDateString('en-LK', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <article className="rounded-lg border border-gray-200 p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <StarRating rating={rating} size="sm" />
            <h4 className="text-sm font-semibold text-gray-900">{title}</h4>
          </div>
          <div className="mt-1 flex items-center gap-2 text-xs text-gray-500">
            <span className="font-medium text-gray-700">{userName}</span>
            <span>·</span>
            <time dateTime={createdAt}>{formattedDate}</time>
            {isVerified && (
              <>
                <span>·</span>
                <span className="inline-flex items-center gap-1 text-green-600">
                  <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Verified Purchase
                </span>
              </>
            )}
          </div>
        </div>
      </div>
      {content && (
        <p className="mt-3 text-sm leading-relaxed text-gray-700">{content}</p>
      )}
    </article>
  );
}
