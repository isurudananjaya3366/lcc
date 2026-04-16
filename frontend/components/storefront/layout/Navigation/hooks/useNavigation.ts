'use client';

import { useQuery } from '@tanstack/react-query';
import type { NavigationData } from '../types/navigation';

async function fetchNavigation(): Promise<NavigationData> {
  const response = await fetch('/api/storefront/navigation');

  if (!response.ok) {
    throw new Error('Failed to fetch navigation data');
  }

  return response.json();
}

export function useNavigation() {
  return useQuery<NavigationData>({
    queryKey: ['navigation'],
    queryFn: fetchNavigation,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 3,
  });
}
