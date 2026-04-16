import type { AnnouncementBarConfig } from '@/types/store/layout';

export const announcementColorPresets = {
  primary: { backgroundColor: 'bg-green-700', textColor: 'text-white' },
  success: { backgroundColor: 'bg-emerald-600', textColor: 'text-white' },
  warning: { backgroundColor: 'bg-yellow-500', textColor: 'text-black' },
  info: { backgroundColor: 'bg-blue-600', textColor: 'text-white' },
  sale: { backgroundColor: 'bg-red-600', textColor: 'text-white' },
} as const;

export const defaultAnnouncementConfig: AnnouncementBarConfig = {
  enabled: true,
  message: 'Free delivery on orders over ₨5,000! 🚚',
  link: '/shipping',
  linkText: 'Learn more',
  ...announcementColorPresets.primary,
};

export const announcementTemplates: Record<string, AnnouncementBarConfig> = {
  freeShipping: {
    enabled: true,
    message: 'Free delivery on orders over ₨5,000! 🚚',
    link: '/shipping',
    linkText: 'Learn more',
    ...announcementColorPresets.primary,
  },
  sale: {
    enabled: true,
    message: '🎉 Seasonal Sale — Up to 30% off selected items!',
    link: '/search?sort=sale',
    linkText: 'Shop now',
    ...announcementColorPresets.sale,
  },
  newArrivals: {
    enabled: true,
    message: '✨ New arrivals just landed — check them out!',
    link: '/search?sort=newest',
    linkText: 'View new',
    ...announcementColorPresets.info,
  },
  holiday: {
    enabled: true,
    message: '🎄 Holiday deals are live — limited stock available!',
    link: '/search?category=deals',
    linkText: 'Shop deals',
    ...announcementColorPresets.warning,
  },
};
