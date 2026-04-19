'use client';

import { useQuery } from '@tanstack/react-query';
import * as flashSaleApi from '@/lib/marketing/flash-sale';
import type { FlashSale, FlashSaleListItem } from '@/types/marketing/flash-sale.types';

const FLASH_SALE_KEYS = {
  all: ['flash-sales'] as const,
  list: () => ['flash-sales', 'list'] as const,
  detail: (slug: string) => ['flash-sales', 'detail', slug] as const,
  active: () => ['flash-sales', 'active'] as const,
  featured: () => ['flash-sales', 'featured'] as const,
};

export function useFlashSales() {
  return useQuery<FlashSaleListItem[]>({
    queryKey: FLASH_SALE_KEYS.list(),
    queryFn: () => flashSaleApi.getFlashSales(),
    staleTime: 60 * 1000,
  });
}

export function useFlashSaleDetail(slug: string) {
  return useQuery<FlashSale>({
    queryKey: FLASH_SALE_KEYS.detail(slug),
    queryFn: () => flashSaleApi.getFlashSaleBySlug(slug),
    enabled: !!slug,
    staleTime: 30 * 1000,
  });
}

export function useActiveFlashSales() {
  return useQuery<FlashSaleListItem[]>({
    queryKey: FLASH_SALE_KEYS.active(),
    queryFn: () => flashSaleApi.getActiveFlashSales(),
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
  });
}

export function useFeaturedFlashProducts() {
  return useQuery({
    queryKey: FLASH_SALE_KEYS.featured(),
    queryFn: () => flashSaleApi.getFeaturedFlashSaleProducts(),
    staleTime: 60 * 1000,
  });
}
