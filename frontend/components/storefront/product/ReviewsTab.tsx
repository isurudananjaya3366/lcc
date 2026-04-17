'use client';

import { useState } from 'react';
import { useProductReviews, useReviewStats } from '@/hooks/queries/useStoreProducts';
import { ReviewsSummary } from './ReviewsSummary';
import { ReviewList } from './ReviewList';
import { WriteReviewButton } from './WriteReviewButton';

const PAGE_SIZE = 5;

interface ReviewsTabProps {
  productId: number;
}

export function ReviewsTab({ productId }: ReviewsTabProps) {
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const { data: reviews, isLoading: reviewsLoading } = useProductReviews(productId);
  const { data: stats, isLoading: statsLoading } = useReviewStats(productId);

  if (reviewsLoading || statsLoading) {
    return (
      <div className="space-y-4">
        <div className="h-32 animate-pulse rounded-lg bg-gray-100" />
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-24 animate-pulse rounded-lg bg-gray-100" />
          ))}
        </div>
      </div>
    );
  }

  const allReviews = reviews?.results ?? [];
  const visibleReviews = allReviews.slice(0, visibleCount);
  const hasMore = visibleCount < allReviews.length;

  return (
    <div className="space-y-8">
      {stats && (
        <ReviewsSummary stats={stats} />
      )}

      <WriteReviewButton productId={productId} />

      {allReviews.length > 0 ? (
        <>
          <ReviewList reviews={visibleReviews} />
          {hasMore && (
            <div className="flex justify-center">
              <button
                onClick={() => setVisibleCount((prev) => prev + PAGE_SIZE)}
                className="rounded-lg border border-gray-300 px-6 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Load more reviews
              </button>
            </div>
          )}
          {!hasMore && allReviews.length > PAGE_SIZE && (
            <p className="text-center text-sm text-gray-400">All reviews loaded</p>
          )}
        </>
      ) : (
        <p className="text-center text-sm text-gray-500 py-8">
          No reviews yet. Be the first to review this product!
        </p>
      )}
    </div>
  );
}
