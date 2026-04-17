'use client';

import { StarRating } from './StarRating';
import { ReviewCountLink } from './ReviewCountLink';

interface RatingSummaryProps {
  rating: number;
  reviewCount: number;
  productId: number;
}

export function RatingSummary({ rating, reviewCount, productId }: RatingSummaryProps) {
  if (reviewCount === 0) {
    return (
      <div className="flex items-center gap-2">
        <StarRating rating={0} />
        <span className="text-sm text-gray-500">No reviews yet</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <StarRating rating={rating} />
      <span className="text-sm font-medium text-gray-700">{rating.toFixed(1)}</span>
      <ReviewCountLink count={reviewCount} productId={productId} />
    </div>
  );
}
