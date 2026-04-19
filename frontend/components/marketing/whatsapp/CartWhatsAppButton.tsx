'use client';

import { WhatsAppButton } from './WhatsAppButton';

interface CartItem {
  name: string;
  quantity: number;
  price: number;
}

interface CartWhatsAppButtonProps {
  items: CartItem[];
  total: number;
  couponCode?: string;
  className?: string;
}

export function CartWhatsAppButton({ items, total, couponCode, className = '' }: CartWhatsAppButtonProps) {
  return (
    <WhatsAppButton
      messageType="cart_share"
      data={{ items, total, couponCode }}
      label="Order via WhatsApp"
      variant="primary"
      size="md"
      className={className}
    />
  );
}
