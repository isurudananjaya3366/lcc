/**
 * Coupon System Types
 */

export type DiscountType = 'percentage' | 'fixed_amount' | 'free_shipping';

export type CouponStatus = 'active' | 'expired' | 'inactive' | 'exhausted' | 'scheduled';

export interface CouponRestrictions {
  minimumOrder?: number;
  maximumDiscount?: number;
  applicableProducts?: string[];
  applicableCategories?: string[];
  excludedProducts?: string[];
  excludedCategories?: string[];
  firstOrderOnly?: boolean;
  usageLimitPerUser?: number;
  totalUsageLimit?: number;
}

export interface Coupon {
  id: string;
  code: string;
  title: string;
  description: string;
  discountType: DiscountType;
  discountValue: number;
  restrictions: CouponRestrictions;
  status: CouponStatus;
  startDate: string;
  endDate: string;
  usageCount: number;
  createdAt: string;
}

export interface ValidateCouponRequest {
  code: string;
  cartTotal: number;
  items: Array<{ productId: string; categoryId: string; quantity: number; price: number }>;
  userId?: string;
}

export interface ValidateCouponResponse {
  valid: boolean;
  coupon?: Coupon;
  discount?: number;
  message?: string;
  validationDetails?: {
    minimumOrderMet: boolean;
    productRestrictionsMet: boolean;
    usageLimitMet: boolean;
    expiryValid: boolean;
  };
}

export interface ApplyCouponRequest {
  code: string;
  cartId?: string;
}

export interface ApplyCouponResponse {
  success: boolean;
  appliedCoupon?: Coupon;
  discount: number;
  originalTotal: number;
  newTotal: number;
  appliedAt: string;
}

export interface RemoveCouponRequest {
  cartId?: string;
}

export interface RemoveCouponResponse {
  success: boolean;
  restoredTotal: number;
  previousDiscount: number;
}

export interface CouponFormData {
  code: string;
}

export interface CouponListItem {
  id: string;
  code: string;
  description: string;
  discountType: DiscountType;
  discountValue: number;
  minimumOrder?: number;
  endDate: string;
  isApplicable: boolean;
}

export interface CouponSummary {
  code: string;
  discountType: DiscountType;
  discountValue: number;
  discountAmount: number;
}
