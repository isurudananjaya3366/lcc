'use client';

import { useState, useEffect, useCallback } from 'react';
import { useStoreAuthStore } from '@/stores/store';
import {
  getOrders,
  getAddresses,
  getWishlist,
  getMyReviews,
} from '@/services/storefront/portalService';
import type {
  PortalOrder,
  PortalAddress,
  WishlistItem,
  PortalReview,
} from '@/types/storefront/portal.types';

interface PortalSummary {
  orderCount: number;
  addressCount: number;
  wishlistCount: number;
  reviewCount: number;
  recentOrders: PortalOrder[];
}

interface UsePortalReturn {
  summary: PortalSummary | null;
  addresses: PortalAddress[];
  wishlistItems: WishlistItem[];
  reviews: PortalReview[];
  isLoading: boolean;
  error: string | null;
  refresh: () => void;
}

const EMPTY_SUMMARY: PortalSummary = {
  orderCount: 0,
  addressCount: 0,
  wishlistCount: 0,
  reviewCount: 0,
  recentOrders: [],
};

/**
 * Convenience hook that aggregates all customer portal data.
 * Hydrates on mount when authenticated.
 */
export function usePortal(): UsePortalReturn {
  const isAuthenticated = useStoreAuthStore((s) => s.isAuthenticated);

  const [summary, setSummary] = useState<PortalSummary | null>(null);
  const [addresses, setAddresses] = useState<PortalAddress[]>([]);
  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [reviews, setReviews] = useState<PortalReview[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!isAuthenticated) return;

    setIsLoading(true);
    setError(null);

    try {
      const [ordersRes, addressData, wishlistData, reviewData] =
        await Promise.allSettled([
          getOrders({ page: 1, pageSize: 5 }),
          getAddresses(),
          getWishlist(),
          getMyReviews(),
        ]);

      const orders =
        ordersRes.status === 'fulfilled' ? ordersRes.value : { orders: [], total: 0 };
      const addressList =
        addressData.status === 'fulfilled' ? addressData.value : [];
      const wishlist =
        wishlistData.status === 'fulfilled' ? wishlistData.value : [];
      const reviewList =
        reviewData.status === 'fulfilled' ? reviewData.value : [];

      setAddresses(addressList);
      setWishlistItems(wishlist);
      setReviews(reviewList);
      setSummary({
        orderCount: orders.total,
        addressCount: addressList.length,
        wishlistCount: wishlist.length,
        reviewCount: reviewList.length,
        recentOrders: orders.orders,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load portal data');
      setSummary(EMPTY_SUMMARY);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return {
    summary,
    addresses,
    wishlistItems,
    reviews,
    isLoading,
    error,
    refresh: loadData,
  };
}
