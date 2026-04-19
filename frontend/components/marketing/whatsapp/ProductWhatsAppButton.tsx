'use client';

import { WhatsAppButton } from './WhatsAppButton';

interface ProductWhatsAppButtonProps {
  productName: string;
  price: number;
  sku?: string;
  className?: string;
}

export function ProductWhatsAppButton({ productName, price, sku, className = '' }: ProductWhatsAppButtonProps) {
  const productUrl = typeof window !== 'undefined' ? window.location.href : '';

  return (
    <WhatsAppButton
      messageType="product_inquiry"
      data={{ productName, price, sku, productUrl }}
      label="Ask about this product"
      variant="outline"
      size="sm"
      className={className}
    />
  );
}
