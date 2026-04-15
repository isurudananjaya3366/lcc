/**
 * useVendors — fetch paginated vendor list
 */

import { useQuery } from '@tanstack/react-query';
import { customerKeys } from '@/lib/queryKeys';
import vendorService from '@/services/api/vendorService';

interface VendorFilters {
  search?: string;
  status?: 'all' | 'active' | 'inactive';
  category?: string;
  paymentStatus?: 'all' | 'current' | 'overdue';
  sortBy?: 'name' | 'created' | 'lastPurchase' | 'totalPurchased';
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}

export type { VendorFilters };

export function useVendors(filters?: VendorFilters) {
  return useQuery({
    // Vendors don't have their own top-level key factory; use a manual key
    queryKey: ['vendors', 'list', filters] as const,
    queryFn: () =>
      vendorService.getVendors(filters as Parameters<typeof vendorService.getVendors>[0]),
    staleTime: 5 * 60 * 1000,
    placeholderData: (prev) => prev,
    refetchOnWindowFocus: true,
  });
}
