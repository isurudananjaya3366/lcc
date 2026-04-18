'use client';

import { Star } from 'lucide-react';
import { cn } from '@/lib/cn';

interface StarRatingProps {
  rating: number;
  maxStars?: number;
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  onChange?: (rating: number) => void;
}

const sizeMap = {
  sm: 'h-3.5 w-3.5',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
};

export function StarRating({
  rating,
  maxStars = 5,
  size = 'md',
  interactive = false,
  onChange,
}: StarRatingProps) {
  return (
    <div className="flex items-center gap-0.5">
      {Array.from({ length: maxStars }, (_, i) => {
        const starIndex = i + 1;
        const isFilled = starIndex <= rating;
        return (
          <Star
            key={i}
            className={cn(
              sizeMap[size],
              isFilled ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300',
              interactive && 'cursor-pointer hover:text-yellow-400'
            )}
            onClick={interactive && onChange ? () => onChange(starIndex) : undefined}
          />
        );
      })}
    </div>
  );
}
