'use client';

import React, { type FC } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import type { FeaturedImageProps } from './types/navigation';

const aspectRatioClasses: Record<string, string> = {
  '16/9': 'aspect-video',
  '4/3': 'aspect-[4/3]',
  '1/1': 'aspect-square',
  '3/2': 'aspect-[3/2]',
};

const FeaturedImage: FC<FeaturedImageProps> = ({
  src,
  alt,
  aspectRatio = '16/9',
  priority = false,
  className,
}) => {
  return (
    <div
      className={cn(
        'relative overflow-hidden rounded-lg',
        aspectRatioClasses[aspectRatio],
        'group',
        className
      )}
    >
      <Image
        src={src}
        alt={alt}
        fill
        sizes="(max-width: 768px) 100vw, 25vw"
        className="object-cover transition-transform duration-300 group-hover:scale-105"
        priority={priority}
      />
    </div>
  );
};

export default FeaturedImage;
