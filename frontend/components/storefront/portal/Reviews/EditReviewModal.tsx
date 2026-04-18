'use client';

import { useState, useEffect } from 'react';
import type { PortalReview } from '@/types/storefront/portal.types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { StarRating } from './StarRating';

interface EditReviewModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  review: PortalReview;
  onSave: (id: string, data: { rating: number; title: string; content: string }) => void;
}

export function EditReviewModal({ open, onOpenChange, review, onSave }: EditReviewModalProps) {
  const [rating, setRating] = useState(review.rating);
  const [title, setTitle] = useState(review.title);
  const [content, setContent] = useState(review.content);

  useEffect(() => {
    setRating(review.rating);
    setTitle(review.title);
    setContent(review.content);
  }, [review]);

  const handleSave = () => {
    onSave(review.id, { rating, title, content });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Review</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Rating</label>
            <StarRating rating={rating} interactive onChange={setRating} />
          </div>
          <div className="space-y-2">
            <label htmlFor="review-title" className="text-sm font-medium">
              Title
            </label>
            <Input
              id="review-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Review title"
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="review-content" className="text-sm font-medium">
              Content
            </label>
            <Textarea
              id="review-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your review..."
              rows={4}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!title.trim() || !content.trim() || rating === 0}>
            Save Changes
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
