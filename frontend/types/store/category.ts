/**
 * Storefront Category Types
 */

export interface StoreCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  parentId?: string;
  level: number;
  productCount: number;
  isVisible: boolean;
  isLeaf: boolean;
  hasChildren: boolean;
  sortOrder: number;
}

export interface StoreCategoryTree {
  id: string;
  name: string;
  slug: string;
  image?: string;
  children: StoreCategoryTree[];
  productCount: number;
}

export interface StoreCategoryBreadcrumb {
  name: string;
  slug: string;
  url: string;
}

export interface StoreCategoryFilters {
  level?: number;
  parentId?: string;
  hasProducts?: boolean;
  isVisible?: boolean;
}
