import { getStoreClient, type PaginatedResponse } from '../client';

// ─── Types ──────────────────────────────────────────────────────────────────

export interface ReviewAuthor {
  user_id: number;
  first_name: string;
  last_name: string;
  avatar_url: string | null;
  review_count: number;
  is_verified_buyer: boolean;
}

export interface Review {
  id: number;
  product_id: number;
  user_id: number;
  order_item_id: number | null;
  rating: number;
  title: string;
  content: string;
  is_verified_purchase: boolean;
  helpful_count: number;
  not_helpful_count: number;
  images: string[];
  response: { content: string; responded_at: string } | null;
  author: ReviewAuthor;
  created_at: string;
  updated_at: string;
}

export interface ReviewStats {
  average_rating: number;
  total_reviews: number;
  rating_distribution: Record<number, number>;
  verified_purchase_percentage: number;
  recommendation_percentage: number;
}

export interface CreateReviewParams {
  product_id: number;
  order_item_id?: number;
  rating: number;
  title: string;
  content: string;
  images?: string[];
  recommend?: boolean;
}

export interface UpdateReviewParams {
  rating?: number;
  title?: string;
  content?: string;
  images?: string[];
}

export interface ReviewsListParams {
  rating?: number;
  verified_only?: boolean;
  sort?: 'newest' | 'oldest' | 'highest' | 'lowest' | 'most_helpful';
  page?: number;
  page_size?: number;
}

// ─── Cache ──────────────────────────────────────────────────────────────────

const statsCache = new Map<string, { data: ReviewStats; expiry: number }>();
const STATS_CACHE_TTL = 5 * 60 * 1000;

// ─── Validation Utilities ───────────────────────────────────────────────────

export function validateRating(rating: number): boolean {
  return Number.isInteger(rating) && rating >= 1 && rating <= 5;
}

export function validateReviewTitle(title: string): boolean {
  return title.length >= 3 && title.length <= 200;
}

export function formatRating(rating: number, style: 'stars' | 'number' = 'number'): string {
  if (style === 'stars') {
    const full = Math.floor(rating);
    const empty = 5 - full;
    return '★'.repeat(full) + '☆'.repeat(empty);
  }
  return rating.toFixed(1);
}

export function getAverageRating(reviews: Review[]): number {
  if (reviews.length === 0) return 0;
  const sum = reviews.reduce((acc, r) => acc + r.rating, 0);
  return Math.round((sum / reviews.length) * 10) / 10;
}

// ─── API Functions ──────────────────────────────────────────────────────────

export async function getProductReviews(
  productId: number,
  params?: ReviewsListParams
): Promise<PaginatedResponse<Review>> {
  const { data } = await getStoreClient().get(`/products/${productId}/reviews/`, { params });
  return data;
}

export async function getReviewStats(productId: number): Promise<ReviewStats> {
  const cacheKey = `review-stats-${productId}`;
  const cached = statsCache.get(cacheKey);
  if (cached && Date.now() < cached.expiry) return cached.data;

  const { data } = await getStoreClient().get(`/products/${productId}/reviews/stats/`);
  statsCache.set(cacheKey, { data, expiry: Date.now() + STATS_CACHE_TTL });
  return data;
}

export async function createReview(params: CreateReviewParams): Promise<Review> {
  const { data } = await getStoreClient().post('/reviews/', params);
  return data;
}

export async function updateReview(reviewId: number, params: UpdateReviewParams): Promise<Review> {
  const { data } = await getStoreClient().put(`/reviews/${reviewId}/`, params);
  return data;
}

export async function deleteReview(reviewId: number): Promise<void> {
  await getStoreClient().delete(`/reviews/${reviewId}/`);
}

export async function getMyReviews(params?: {
  product_id?: number;
  rating?: number;
  page?: number;
  page_size?: number;
}): Promise<PaginatedResponse<Review>> {
  const { data } = await getStoreClient().get('/customer/reviews/', { params });
  return data;
}

export async function canReview(
  productId: number
): Promise<{ can_review: boolean; reason?: string }> {
  const { data } = await getStoreClient().get(`/products/${productId}/reviews/can-review/`);
  return data;
}

export async function markReviewHelpful(reviewId: number): Promise<{ helpful_count: number }> {
  const { data } = await getStoreClient().post(`/reviews/${reviewId}/vote/`, { type: 'helpful' });
  return data;
}

export async function markReviewNotHelpful(
  reviewId: number
): Promise<{ not_helpful_count: number }> {
  const { data } = await getStoreClient().post(`/reviews/${reviewId}/vote/`, {
    type: 'not_helpful',
  });
  return data;
}

export async function removeVote(reviewId: number): Promise<void> {
  await getStoreClient().delete(`/reviews/${reviewId}/vote/`);
}

const reviewsApi = {
  getProductReviews,
  getReviewStats,
  createReview,
  updateReview,
  deleteReview,
  getMyReviews,
  canReview,
  markReviewHelpful,
  markReviewNotHelpful,
  removeVote,
  validateRating,
  validateReviewTitle,
  formatRating,
  getAverageRating,
};

export default reviewsApi;
