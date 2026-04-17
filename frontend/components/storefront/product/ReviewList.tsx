import { ReviewCard } from './ReviewCard';

interface ReviewItem {
  id: number;
  user_name?: string;
  rating: number;
  title: string;
  comment?: string;
  content?: string;
  created_at: string;
  verified_purchase?: boolean;
  is_verified_purchase?: boolean;
  author?: { first_name: string; last_name: string };
}

interface ReviewListProps {
  reviews: ReviewItem[];
}

export function ReviewList({ reviews }: ReviewListProps) {
  if (reviews.length === 0) return null;

  return (
    <div className="space-y-4">
      {reviews.map((review) => (
        <ReviewCard
          key={review.id}
          userName={review.author ? `${review.author.first_name} ${review.author.last_name}` : review.user_name ?? 'Anonymous'}
          rating={review.rating}
          title={review.title}
          content={review.content ?? review.comment ?? ''}
          createdAt={review.created_at}
          isVerified={review.is_verified_purchase ?? review.verified_purchase ?? false}
        />
      ))}
    </div>
  );
}
