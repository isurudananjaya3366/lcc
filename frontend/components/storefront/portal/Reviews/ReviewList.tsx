'use client';

import type { PortalReview } from '@/types/storefront/portal.types';
import { ReviewCard } from './ReviewCard';

interface ReviewListProps {
  reviews: PortalReview[];
  onEdit: (review: PortalReview) => void;
  onDelete: (id: string) => void;
}

export function ReviewList({ reviews, onEdit, onDelete }: ReviewListProps) {
  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <ReviewCard key={review.id} review={review} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );
}
