import type { ReactNode } from 'react';

// ─── Header Props ──────────────────────────────────────────────────────────

export interface HeaderProps {
  className?: string;
  storeName?: string;
}

// ─── Logo Props ────────────────────────────────────────────────────────────

export interface LogoProps {
  src?: string;
  alt?: string;
  width?: number;
  height?: number;
  href?: string;
  className?: string;
  priority?: boolean;
}

// ─── Search Props ──────────────────────────────────────────────────────────

export interface SearchProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
}

export interface SearchOverlayProps {
  isOpen: boolean;
  onClose: () => void;
  onSearch?: (query: string) => void;
  placeholder?: string;
}

// ─── Account Props ─────────────────────────────────────────────────────────

export interface AccountMenuProps {
  isLoggedIn: boolean;
  userName?: string;
  userEmail?: string;
  onLogout: () => void;
}

export interface AccountDropdownProps {
  isOpen: boolean;
  isLoggedIn: boolean;
  onClose: () => void;
  userName?: string;
  userEmail?: string;
  className?: string;
}

export interface AccountMenuItem {
  label: string;
  href: string;
  icon?: ReactNode;
  onClick?: () => void;
}

// ─── Cart Props ────────────────────────────────────────────────────────────

export interface HeaderCartItem {
  id: string;
  name: string;
  slug: string;
  price: number;
  quantity: number;
  image: string;
  variant?: string;
}

export interface CartIconProps {
  itemCount: number;
  onClick: () => void;
  className?: string;
  showBadge?: boolean;
}

export interface CartBadgeProps {
  count: number;
  max?: number;
  className?: string;
}

export interface MiniCartProps {
  isOpen: boolean;
  onClose: () => void;
  items: HeaderCartItem[];
  subtotal: number;
  onRemoveItem: (id: string) => void;
  onViewCart: () => void;
  onCheckout: () => void;
}

export interface MiniCartItemProps {
  item: HeaderCartItem;
  onRemove: (id: string) => void;
  className?: string;
}

export interface MiniCartFooterProps {
  subtotal: number;
  onViewCart: () => void;
  onCheckout: () => void;
  itemCount?: number;
  className?: string;
}

// ─── Wishlist Props ────────────────────────────────────────────────────────

export interface WishlistIconProps {
  itemCount: number;
  isActive?: boolean;
  onClick?: () => void;
  href?: string;
  showBadge?: boolean;
  className?: string;
}

// ─── Header Actions ────────────────────────────────────────────────────────

export interface HeaderActionsProps {
  className?: string;
  showSearch?: boolean;
  showWishlist?: boolean;
}

// ─── Utility Types ─────────────────────────────────────────────────────────

export type HeaderSection = 'left' | 'center' | 'right';
export type HeaderSize = 'sm' | 'md' | 'lg';
