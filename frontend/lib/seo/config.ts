import type { SEOConfig } from './types';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://store.lk';

export const seoConfig: SEOConfig = {
  siteName: 'Ceylon Store',
  siteUrl,
  defaultTitle: 'Ceylon Store - Authentic Sri Lankan Products',
  titleTemplate: '%s | Ceylon Store',
  defaultDescription:
    'Discover authentic Sri Lankan products including Ceylon cinnamon, tea, spices, handcrafts and more. Free delivery in Colombo for orders over ₨5,000.',
  defaultImage: `${siteUrl}/images/og-default.jpg`,
  twitterHandle: '@ceylonstore',
  locale: 'en_US',
  themeColor: '#16a34a',
};
