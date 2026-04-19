/**
 * Flash Sale & Limited-Time Offer Types
 */

export type FlashSaleStatus = 'upcoming' | 'active' | 'ending_soon' | 'ended' | 'paused' | 'cancelled';

export const FLASH_SALE_STATUS = {
  SCHEDULED: 'upcoming',
  ACTIVE: 'active',
  ENDING_SOON: 'ending_soon',
  EXPIRED: 'ended',
  CANCELLED: 'cancelled',
} as const;

export type DiscountType = 'percentage' | 'fixed_amount';

export interface DiscountConfig {
  type: DiscountType;
  value: number;
  maxDiscount?: number;
}

export type SeasonalSaleType = 'avurudu' | 'vesak' | 'christmas' | 'eid' | 'new_year' | 'black_friday';

export interface FlashSaleProduct {
  id: string;
  productId: string;
  name: string;
  slug: string;
  image: string;
  originalPrice: number;
  salePrice: number;
  discountPercentage: number;
  totalStock: number;
  soldCount: number;
  remainingStock: number;
  limitPerCustomer: number;
}

export interface FlashSale {
  id: string;
  title: string;
  description: string;
  slug: string;
  bannerImage?: string;
  startDate: string;
  endDate: string;
  status: FlashSaleStatus;
  products: FlashSaleProduct[];
  totalProducts: number;
  createdAt: string;
}

export interface FlashSaleListItem {
  id: string;
  title: string;
  slug: string;
  bannerImage?: string;
  startDate: string;
  endDate: string;
  status: FlashSaleStatus;
  totalProducts: number;
  discountRange: { min: number; max: number };
}

export interface CountdownTime {
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  isExpired: boolean;
  totalSeconds: number;
}

export interface FlashSaleListResponse {
  results: FlashSaleListItem[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface FlashSaleDetailResponse {
  sale: FlashSale;
  relatedSales: FlashSaleListItem[];
}

export interface FlashSaleFilter {
  status?: FlashSaleStatus;
  seasonal?: SeasonalSaleType;
  minDiscount?: number;
  search?: string;
}
