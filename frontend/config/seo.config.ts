/**
 * SEO Defaults Configuration
 *
 * Default meta tags, structured data templates, and SEO settings.
 */

export const seoConfig = {
  defaults: {
    titleTemplate: '%s | LankaCommerce Cloud',
    titleSeparator: '|',
    maxTitleLength: 60,
    maxDescriptionLength: 160,
    defaultTitle: 'LankaCommerce Cloud | Sri Lankan E-Commerce Platform',
    defaultDescription:
      'Shop quality products from Sri Lanka. Electronics, fashion, home & garden, and more with secure checkout and fast delivery island-wide.',
    defaultImage: '/images/og-default.jpg',
    imageWidth: 1200,
    imageHeight: 630,
  },

  openGraph: {
    type: 'website',
    locale: 'en_LK',
    siteName: 'LankaCommerce Cloud',
  },

  twitter: {
    card: 'summary_large_image' as const,
    site: '@lankacommerce',
  },

  robots: {
    index: true,
    follow: true,
    noindexPaths: ['/cart', '/checkout', '/account', '/api/internal'],
  },

  structuredData: {
    organization: {
      '@type': 'Organization',
      name: 'LankaCommerce Cloud',
      url: 'https://lankacommerce.lk',
      logo: 'https://lankacommerce.lk/images/logo.svg',
      contactPoint: {
        '@type': 'ContactPoint',
        telephone: '+94-11-234-5678',
        contactType: 'customer service',
        areaServed: 'LK',
        availableLanguage: ['English', 'Sinhala', 'Tamil'],
      },
    },

    localBusiness: {
      '@type': 'LocalBusiness',
      name: 'LankaCommerce Cloud (Pvt) Ltd',
      address: {
        '@type': 'PostalAddress',
        streetAddress: '123 Galle Road',
        addressLocality: 'Colombo',
        addressRegion: 'Western',
        postalCode: '00300',
        addressCountry: 'LK',
      },
    },
  },

  sitemap: {
    changeFrequency: {
      homepage: 'daily',
      products: 'daily',
      categories: 'weekly',
      content: 'monthly',
    },
  },

  robotsTxt: {
    allow: ['/'],
    disallow: ['/admin', '/api/internal', '/account', '/checkout', '/cart'],
    sitemap: '/sitemap.xml',
  },
} as const;
