'use client';

import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import type { PortalReview } from '@/types/storefront/portal.types';
import { getMyReviews, deleteReview, updateReview } from '@/services/storefront/portalService';
import { ReviewList } from './ReviewList';
import { EmptyReviews } from './EmptyReviews';
import { EditReviewModal } from './EditReviewModal';
import { DeleteReviewDialog } from './DeleteReviewDialog';
import { ReviewsHeader } from './ReviewsHeader';
import { Loader2 } from 'lucide-react';

export function ReviewsPage() {
  const [reviews, setReviews] = useState<PortalReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingReview, setEditingReview] = useState<PortalReview | null>(null);
  const [deleteReviewId, setDeleteReviewId] = useState<string | null>(null);

  useEffect(() => {
    getMyReviews()
      .then(setReviews)
      .catch(() => toast.error('Failed to load reviews'))
      .finally(() => setLoading(false));
  }, []);

  const handleEdit = (review: PortalReview) => {
    setEditingReview(review);
  };

  const handleSave = async (id: string, data: { rating: number; title: string; content: string }) => {
    try {
      const updated = await updateReview(id, data);
      setReviews((prev) => prev.map((r) => (r.id === id ? updated : r)));
      setEditingReview(null);
      toast.success('Review updated successfully');
    } catch {
      toast.error('Failed to update review');
    }
  };

  const handleDelete = (id: string) => {
    setDeleteReviewId(id);
  };

  const confirmDelete = async () => {
    if (!deleteReviewId) return;
    try {
      await deleteReview(deleteReviewId);
      setReviews((prev) => prev.filter((r) => r.id !== deleteReviewId));
      setDeleteReviewId(null);
      toast.success('Review deleted successfully');
    } catch {
      toast.error('Failed to delete review');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <ReviewsHeader count={reviews.length} />
      {reviews.length > 0 ? (
        <ReviewList reviews={reviews} onEdit={handleEdit} onDelete={handleDelete} />
      ) : (
        <EmptyReviews />
      )}
      {editingReview && (
        <EditReviewModal
          open={!!editingReview}
          onOpenChange={(open) => !open && setEditingReview(null)}
          review={editingReview}
          onSave={handleSave}
        />
      )}
      <DeleteReviewDialog
        open={!!deleteReviewId}
        onOpenChange={(open) => !open && setDeleteReviewId(null)}
        onConfirm={confirmDelete}
      />
    </div>
  );
}
