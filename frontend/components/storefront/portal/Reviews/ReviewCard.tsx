'use client';

import Link from 'next/link';
import Image from 'next/image';
import { Pencil, Trash2, ExternalLink } from 'lucide-react';
import type { PortalReview } from '@/types/storefront/portal.types';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { StarRating } from './StarRating';

interface ReviewCardProps {
  review: PortalReview;
  onEdit: (review: PortalReview) => void;
  onDelete: (id: string) => void;
}

export function ReviewCard({ review, onEdit, onDelete }: ReviewCardProps) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex gap-4">
          <Link href={`/products/${review.productSlug}`} className="shrink-0">
            <div className="relative h-16 w-16 rounded-md overflow-hidden bg-muted">
              <Image
                src={review.productImage}
                alt={review.productName}
                fill
                className="object-cover"
                sizes="64px"
              />
            </div>
          </Link>
          <div className="flex-1 min-w-0 space-y-1">
            <div className="flex items-start justify-between gap-2">
              <Link
                href={`/products/${review.productSlug}`}
                className="font-medium text-sm hover:underline line-clamp-1"
              >
                {review.productName}
              </Link>
              <Badge variant={review.isPublished ? 'default' : 'secondary'} className="text-xs shrink-0">
                {review.isPublished ? 'Published' : 'Draft'}
              </Badge>
            </div>
            <StarRating rating={review.rating} size="sm" />
            <h4 className="font-semibold text-sm">{review.title}</h4>
            <p className="text-sm text-muted-foreground line-clamp-3">{review.content}</p>
            <p className="text-xs text-muted-foreground">
              {new Date(review.createdAt).toLocaleDateString()}
              {review.updatedAt !== review.createdAt && ' (edited)'}
            </p>
          </div>
        </div>
        <div className="flex gap-2 mt-3 justify-end">
          <Button size="sm" variant="ghost" onClick={() => onEdit(review)}>
            <Pencil className="h-3.5 w-3.5 mr-1" />
            Edit
          </Button>
          <Button size="sm" variant="ghost" onClick={() => onDelete(review.id)}>
            <Trash2 className="h-3.5 w-3.5 mr-1" />
            Delete
          </Button>
          <Button size="sm" variant="ghost" asChild>
            <Link href={`/products/${review.productSlug}`}>
              <ExternalLink className="h-3.5 w-3.5 mr-1" />
              View Product
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
