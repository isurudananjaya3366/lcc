import type { ReviewStats } from '@/lib/api/store/modules/reviews';
import { StarRating } from './StarRating';
import { RatingBreakdown } from './RatingBreakdown';

interface ReviewsSummaryProps {
  stats: ReviewStats;
}

export function ReviewsSummary({ stats }: ReviewsSummaryProps) {
  return (
    <div className="flex flex-col gap-6 rounded-lg bg-gray-50 p-6 sm:flex-row sm:items-start">
      {/* Average rating */}
      <div className="flex flex-col items-center text-center sm:min-w-[120px]">
        <span className="text-4xl font-bold text-gray-900">
          {stats.average_rating.toFixed(1)}
        </span>
        <StarRating rating={stats.average_rating} size="lg" />
        <span className="mt-1 text-sm text-gray-500">
          {stats.total_reviews} {stats.total_reviews === 1 ? 'review' : 'reviews'}
        </span>
      </div>

      {/* Rating breakdown */}
      <div className="flex-1">
        <RatingBreakdown
          distribution={stats.rating_distribution}
          totalReviews={stats.total_reviews}
        />
      </div>
    </div>
  );
}
