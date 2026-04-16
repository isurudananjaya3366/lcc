'use client';

import React, { useState, type FC } from 'react';
import { cn } from '@/lib/utils';
import type { HeaderActionsProps } from '@/types/store/header';
import SearchIconButton from './SearchIconButton';
import SearchOverlay from './SearchOverlay';
import AccountLink from './AccountLink';
import AccountDropdown from './AccountDropdown';
import CartIcon from './CartIcon';
import MiniCart from './MiniCart';
import WishlistIcon from './WishlistIcon';

const HeaderActions: FC<HeaderActionsProps> = ({
  className,
  showSearch = true,
  showWishlist = true,
}) => {
  const [searchOpen, setSearchOpen] = useState(false);
  const [accountOpen, setAccountOpen] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);

  // TODO: Wire to actual auth state
  const isLoggedIn = false;
  const userName = undefined;
  const userEmail = undefined;

  // TODO: Wire to actual cart state via useCart
  const cartItems: never[] = [];
  const cartSubtotal = 0;

  // TODO: Wire to actual wishlist count
  const wishlistCount = 0;

  return (
    <div className={cn('flex items-center gap-1', className)}>
      {/* Search toggle (mobile) */}
      {showSearch && <SearchIconButton onClick={() => setSearchOpen(true)} />}

      {/* Search overlay */}
      <SearchOverlay isOpen={searchOpen} onClose={() => setSearchOpen(false)} />

      {/* Wishlist (desktop only) */}
      {showWishlist && <WishlistIcon itemCount={wishlistCount} isActive={wishlistCount > 0} />}

      {/* Account */}
      <div className="relative">
        <AccountLink
          isLoggedIn={isLoggedIn}
          userName={userName}
          onClick={() => setAccountOpen(!accountOpen)}
        />
        <AccountDropdown
          isOpen={accountOpen}
          isLoggedIn={isLoggedIn}
          onClose={() => setAccountOpen(false)}
          userName={userName}
          userEmail={userEmail}
        />
      </div>

      {/* Cart */}
      <div className="relative">
        <CartIcon itemCount={cartItems.length} onClick={() => setCartOpen(!cartOpen)} />
        <MiniCart
          isOpen={cartOpen}
          onClose={() => setCartOpen(false)}
          items={cartItems}
          subtotal={cartSubtotal}
          onRemoveItem={() => {}}
          onViewCart={() => {
            setCartOpen(false);
            window.location.href = '/cart';
          }}
          onCheckout={() => {
            setCartOpen(false);
            window.location.href = '/checkout';
          }}
        />
      </div>
    </div>
  );
};

export default HeaderActions;
