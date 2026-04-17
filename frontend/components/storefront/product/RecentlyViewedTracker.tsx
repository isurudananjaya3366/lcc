'use client';

import { useEffect } from 'react';
import { addToRecentlyViewed } from './RecentlyViewed';

interface RecentlyViewedTrackerProps {
  product: {
    slug: string;
    name: string;
    price: number;
    currency: string;
    image: string;
  };
}

export function RecentlyViewedTracker({ product }: RecentlyViewedTrackerProps) {
  useEffect(() => {
    addToRecentlyViewed(product);
  }, [product]);

  return null;
}
