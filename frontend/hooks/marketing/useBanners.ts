'use client';

import { useQuery } from '@tanstack/react-query';
import * as bannerApi from '@/lib/marketing/banner';
import type { Banner, BannerPosition } from '@/types/marketing/banner.types';

const BANNER_KEYS = {
  all: ['banners'] as const,
  position: (pos: BannerPosition) => ['banners', pos] as const,
  active: () => ['banners', 'active'] as const,
  hero: () => ['banners', 'hero'] as const,
};

export function useBannersByPosition(position: BannerPosition) {
  return useQuery<Banner[]>({
    queryKey: BANNER_KEYS.position(position),
    queryFn: () => bannerApi.getBannersByPosition(position),
    staleTime: 5 * 60 * 1000,
  });
}

export function useActiveBanners() {
  return useQuery<Banner[]>({
    queryKey: BANNER_KEYS.active(),
    queryFn: () => bannerApi.getActiveBanners(),
    staleTime: 5 * 60 * 1000,
  });
}

export function useHeroBanners() {
  return useQuery<Banner[]>({
    queryKey: BANNER_KEYS.hero(),
    queryFn: () => bannerApi.getHeroBanners(),
    staleTime: 5 * 60 * 1000,
  });
}
