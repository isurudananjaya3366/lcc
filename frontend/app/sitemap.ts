import type { MetadataRoute } from 'next';

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://store.lk';

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date().toISOString();

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: siteUrl, lastModified: now, changeFrequency: 'daily', priority: 1.0 },
    { url: `${siteUrl}/about`, lastModified: now, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${siteUrl}/contact`, lastModified: now, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${siteUrl}/faq`, lastModified: now, changeFrequency: 'monthly', priority: 0.4 },
    { url: `${siteUrl}/blog`, lastModified: now, changeFrequency: 'weekly', priority: 0.7 },
    { url: `${siteUrl}/terms`, lastModified: now, changeFrequency: 'yearly', priority: 0.3 },
    { url: `${siteUrl}/privacy`, lastModified: now, changeFrequency: 'yearly', priority: 0.3 },
    { url: `${siteUrl}/returns`, lastModified: now, changeFrequency: 'yearly', priority: 0.3 },
    { url: `${siteUrl}/shipping`, lastModified: now, changeFrequency: 'monthly', priority: 0.4 },
    { url: `${siteUrl}/products`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${siteUrl}/search`, lastModified: now, changeFrequency: 'daily', priority: 0.6 },
  ];

  // Mock product pages - in production, fetch from API
  const mockProductSlugs = [
    'ceylon-cinnamon-sticks',
    'ceylon-tea-collection',
    'handwoven-basket',
    'coconut-shell-bowl',
    'batik-fabric-piece',
    'brass-oil-lamp',
  ];
  const productPages: MetadataRoute.Sitemap = mockProductSlugs.map((slug) => ({
    url: `${siteUrl}/products/${slug}`,
    lastModified: now,
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  // Mock category pages
  const mockCategorySlugs = [
    'spices',
    'tea',
    'handcrafts',
    'home-decor',
    'food-beverages',
    'health-wellness',
  ];
  const categoryPages: MetadataRoute.Sitemap = mockCategorySlugs.map((slug) => ({
    url: `${siteUrl}/products?category=${slug}`,
    lastModified: now,
    changeFrequency: 'weekly' as const,
    priority: 0.75,
  }));

  // Mock collection pages
  const mockCollectionSlugs = [
    'new-arrivals',
    'best-sellers',
    'featured',
    'sale',
    'gifts',
  ];
  const collectionPages: MetadataRoute.Sitemap = mockCollectionSlugs.map((slug) => ({
    url: `${siteUrl}/collections/${slug}`,
    lastModified: now,
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }));

  // Mock blog posts
  const mockBlogSlugs = [
    'ceylon-cinnamon-guide',
    'traditional-sri-lankan-crafts',
    'top-10-gift-ideas',
    'sustainable-packaging',
  ];
  const blogPages: MetadataRoute.Sitemap = mockBlogSlugs.map((slug) => ({
    url: `${siteUrl}/blog/${slug}`,
    lastModified: now,
    changeFrequency: 'monthly' as const,
    priority: 0.6,
  }));

  return [...staticPages, ...productPages, ...categoryPages, ...collectionPages, ...blogPages];
}
