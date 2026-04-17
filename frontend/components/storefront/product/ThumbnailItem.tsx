'use client';

import Image from 'next/image';
import type { ProductImage } from '@/lib/api/store/modules/products';

interface ThumbnailItemProps {
  image: ProductImage;
  isSelected: boolean;
  onClick: () => void;
}

export function ThumbnailItem({ image, isSelected, onClick }: ThumbnailItemProps) {
  return (
    <button
      onClick={onClick}
      aria-label={image.alt_text || 'Product thumbnail'}
      aria-pressed={isSelected}
      className={`relative flex-shrink-0 w-16 h-16 rounded-md overflow-hidden border-2 transition-all duration-150 ${
        isSelected
          ? 'border-black ring-1 ring-black/20'
          : 'border-transparent hover:border-gray-300'
      }`}
    >
      <Image
        src={image.url}
        alt={image.alt_text || 'Thumbnail'}
        fill
        sizes="64px"
        className="object-cover"
      />
    </button>
  );
}
