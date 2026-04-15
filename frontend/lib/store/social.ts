/**
 * Store Social Links Configuration
 */

export interface SocialLink {
  platform: string;
  label: string;
  url: string;
  handle?: string;
}

export const socialLinks: SocialLink[] = [
  {
    platform: 'facebook',
    label: 'Facebook',
    url: 'https://facebook.com/lankacommerce',
    handle: '@lankacommerce',
  },
  {
    platform: 'instagram',
    label: 'Instagram',
    url: 'https://instagram.com/lankacommerce',
    handle: '@lankacommerce',
  },
  {
    platform: 'twitter',
    label: 'Twitter / X',
    url: 'https://twitter.com/lankacommerce',
    handle: '@lankacommerce',
  },
  { platform: 'linkedin', label: 'LinkedIn', url: 'https://linkedin.com/company/lankacommerce' },
  { platform: 'youtube', label: 'YouTube', url: 'https://youtube.com/@lankacommerce' },
  { platform: 'whatsapp', label: 'WhatsApp', url: 'https://wa.me/94771234567' },
];

/** Get URL for a specific platform */
export function getSocialUrl(platform: string): string | undefined {
  return socialLinks.find((l) => l.platform === platform)?.url;
}
