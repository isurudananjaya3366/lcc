import type { ReactNode } from 'react';

// ─── Navigation Item Types ─────────────────────────────────────────────────

export interface Subcategory {
  id: string;
  name: string;
  slug: string;
  parentId: string;
}

export interface Featured {
  title: string;
  description: string;
  image: string;
  link: string;
  ctaText: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  children: Subcategory[];
  featured?: Featured;
}

export interface NavigationItem {
  id: string;
  name: string;
  href: string;
  featured?: Featured;
  children?: Category[];
}

export interface NavigationData {
  categories: Category[];
  featured?: Featured;
}

// ─── Component Props ───────────────────────────────────────────────────────

export interface DesktopNavProps {
  items?: NavigationItem[];
  className?: string;
}

export interface NavItemProps {
  item: NavigationItem;
  isActive: boolean;
  hasMegaMenu: boolean;
  children?: ReactNode;
}

export interface NavLinkProps {
  href: string;
  children: ReactNode;
  isActive?: boolean;
  className?: string;
}

export interface SubmenuIndicatorProps {
  isOpen: boolean;
  className?: string;
}

export interface MegaMenuProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
  className?: string;
}

export interface MegaMenuPanelProps {
  categories: Category[];
  featured?: Featured;
  className?: string;
}

export interface MegaMenuCategoriesProps {
  categories: Category[];
  className?: string;
}

export interface CategoryColumnProps {
  category: Category;
  className?: string;
}

export interface MegaMenuFeaturedProps {
  featured: Featured;
  className?: string;
}

export interface FeaturedImageProps {
  src: string;
  alt: string;
  aspectRatio?: '16/9' | '4/3' | '1/1' | '3/2';
  priority?: boolean;
  className?: string;
}
