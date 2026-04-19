'use client';

import { SocialShareButtons } from './SocialShareButtons';
import { buildProductShareData } from '@/lib/marketing/share';

interface ProductShareSectionProps {
  product: {
    name: string;
    slug: string;
    price: number;
    image?: string;
  };
  className?: string;
}

export function ProductShareSection({ product, className = '' }: ProductShareSectionProps) {
  const shareData = buildProductShareData(product);

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <span className="text-sm text-gray-500">Share:</span>
      <SocialShareButtons
        data={shareData}
        platforms={['facebook', 'twitter', 'whatsapp', 'pinterest', 'copy']}
        variant="icons"
      />
    </div>
  );
}
