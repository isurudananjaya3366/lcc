/**
 * Promotional Banner Types
 */

export type BannerPosition = 'hero' | 'sidebar' | 'inline' | 'top-bar' | 'category';
export type BannerType = 'image' | 'text' | 'product' | 'sale' | 'announcement';
export type BannerStatus = 'active' | 'scheduled' | 'expired' | 'disabled';

export interface BannerAction {
  label: string;
  url: string;
  openInNewTab?: boolean;
}

/** Alias: BannerCTA is the same as BannerAction */
export type BannerCTA = BannerAction;

export interface BannerImage {
  url: string;
  alt: string;
  width?: number;
  height?: number;
  mobileUrl?: string;
}

export interface BannerSchedule {
  startDate: string;
  endDate: string;
  timezone?: string;
}

export interface BannerTargeting {
  pages?: string[];
  userSegments?: string[];
  devices?: ('desktop' | 'mobile' | 'tablet')[];
}

export interface BannerResponse {
  banners: Banner[];
  total: number;
}

export interface BannerFilters {
  position?: BannerPosition;
  type?: BannerType;
  status?: BannerStatus;
  search?: string;
}

export interface Banner {
  id: string;
  title: string;
  description?: string;
  type: BannerType;
  position: BannerPosition;
  status: BannerStatus;
  imageUrl?: string;
  mobileImageUrl?: string;
  backgroundColor?: string;
  textColor?: string;
  action?: BannerAction;
  startDate: string;
  endDate: string;
  priority: number;
  isDismissible: boolean;
  createdAt: string;
}

export interface BannerSlide {
  id: string;
  banner: Banner;
  order: number;
}
