'use client';

import { createStore } from '../utils';
import type { FlashSaleListItem } from '@/types/marketing/flash-sale.types';

interface FlashSaleState {
  activeSales: FlashSaleListItem[];
  currentSaleSlug: string | null;
  isLoading: boolean;

  setActiveSales: (sales: FlashSaleListItem[]) => void;
  setCurrentSaleSlug: (slug: string | null) => void;
  setLoading: (loading: boolean) => void;
  reset: () => void;

  getActiveSaleCount: () => number;
}

export const useFlashSaleStore = createStore<FlashSaleState>(
  'flash-sale-store',
  (set, get) => ({
    activeSales: [],
    currentSaleSlug: null,
    isLoading: false,

    setActiveSales: (activeSales) => set({ activeSales }),
    setCurrentSaleSlug: (currentSaleSlug) => set({ currentSaleSlug }),
    setLoading: (isLoading) => set({ isLoading }),
    reset: () => set({ activeSales: [], currentSaleSlug: null, isLoading: false }),

    getActiveSaleCount: () => get().activeSales.filter((s) => s.status === 'active').length,
  }),
  { persist: false }
);
