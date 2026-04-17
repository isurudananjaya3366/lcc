'use client';

import React, { useRef, useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStoreCartStore } from '@/stores/store/cart';
import MiniCartHeader from './MiniCartHeader';
import MiniCartItemsList from './MiniCartItemsList';
import MiniCartSubtotal from './MiniCartSubtotal';
import MiniCartFooter from './MiniCartFooter';
import EmptyMiniCart from './EmptyMiniCart';

interface MiniCartDropdownProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

const MiniCartDropdown: FC<MiniCartDropdownProps> = ({ isOpen, onClose, className }) => {
  const dropdownRef = useRef<HTMLDivElement>(null);
  const items = useStoreCartStore((s) => s.items);
  const getItemCount = useStoreCartStore((s) => s.getItemCount);
  const getSubtotal = useStoreCartStore((s) => s.getSubtotal);
  const removeFromCart = useStoreCartStore((s) => s.removeFromCart);

  const itemCount = getItemCount();
  const subtotal = getSubtotal();

  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={dropdownRef}
      className={cn(
        'absolute right-0 top-full mt-2 w-96 bg-white dark:bg-gray-900 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50',
        'animate-in slide-in-from-top-2 fade-in duration-150',
        className
      )}
      role="dialog"
      aria-label="Shopping cart preview"
    >
      <MiniCartHeader itemCount={itemCount} onClose={onClose} />

      {items.length === 0 ? (
        <EmptyMiniCart />
      ) : (
        <>
          <MiniCartItemsList items={items} onRemoveItem={removeFromCart} />
          <MiniCartSubtotal subtotal={subtotal} />
          <MiniCartFooter />
        </>
      )}
    </div>
  );
};

export default MiniCartDropdown;
