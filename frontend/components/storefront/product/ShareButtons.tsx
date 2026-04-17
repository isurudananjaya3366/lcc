'use client';

import { WhatsAppShare } from './WhatsAppShare';
import { FacebookShare } from './FacebookShare';

interface ShareButtonsProps {
  productName: string;
  productSlug: string;
}

export function ShareButtons({ productName, productSlug }: ShareButtonsProps) {
  const productUrl = typeof window !== 'undefined'
    ? `${window.location.origin}/products/${productSlug}`
    : `/products/${productSlug}`;

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-500">Share:</span>
      <WhatsAppShare productName={productName} productUrl={productUrl} />
      <FacebookShare productUrl={productUrl} />
    </div>
  );
}
