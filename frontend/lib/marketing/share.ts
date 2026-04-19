/**
 * Social Media Sharing Utilities
 */

import type { ShareData, SocialPlatform } from '@/types/marketing/social.types';

const shareUrlBuilders: Record<Exclude<SocialPlatform, 'copy'>, (data: ShareData) => string> = {
  facebook: (data) =>
    `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(data.url)}`,

  twitter: (data) => {
    const params = new URLSearchParams({ url: data.url, text: data.title });
    if (data.hashtags?.length) params.set('hashtags', data.hashtags.join(','));
    return `https://twitter.com/intent/tweet?${params.toString()}`;
  },

  whatsapp: (data) =>
    `https://wa.me/?text=${encodeURIComponent(`${data.title}\n${data.url}`)}`,

  linkedin: (data) =>
    `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(data.url)}`,

  pinterest: (data) => {
    const params = new URLSearchParams({
      url: data.url,
      description: data.title,
    });
    if (data.imageUrl) params.set('media', data.imageUrl);
    return `https://pinterest.com/pin/create/button/?${params.toString()}`;
  },

  email: (data) =>
    `mailto:?subject=${encodeURIComponent(data.title)}&body=${encodeURIComponent(`${data.description || data.title}\n\n${data.url}`)}`,
};

/** Build share URL for a platform */
export function getShareUrl(platform: SocialPlatform, data: ShareData): string {
  if (platform === 'copy') return data.url;
  return shareUrlBuilders[platform](data);
}

/** Open share dialog */
export function openShareDialog(platform: SocialPlatform, data: ShareData): void {
  if (platform === 'copy') {
    navigator.clipboard.writeText(data.url);
    return;
  }

  if (platform === 'email') {
    window.location.href = getShareUrl('email', data);
    return;
  }

  const url = getShareUrl(platform, data);
  window.open(url, '_blank', 'width=600,height=400,noopener,noreferrer');
}

/** Use native share API if available, fallback to custom */
export async function nativeShare(data: ShareData): Promise<boolean> {
  if (typeof navigator !== 'undefined' && navigator.share) {
    try {
      await navigator.share({ title: data.title, text: data.description, url: data.url });
      return true;
    } catch {
      return false;
    }
  }
  return false;
}

/** Build product share data */
export function buildProductShareData(product: { name: string; slug: string; price: number; image?: string }): ShareData {
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  return {
    title: `Check out ${product.name} — ₨${product.price.toLocaleString()}`,
    url: `${baseUrl}/products/${product.slug}`,
    imageUrl: product.image,
    hashtags: ['shopping', 'deals'],
  };
}
