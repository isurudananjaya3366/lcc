// Shared types for Homepage builder components

export interface HomepageSection {
  id: string;
  type: string;
  enabled: boolean;
  order: number;
  settings: Record<string, unknown>;
}

export type SectionType = 'hero' | 'featured' | 'categories' | 'testimonials' | 'newsletter';

export const SECTION_TYPE_LABELS: Record<SectionType, string> = {
  hero: 'Hero Banner',
  featured: 'Featured Products',
  categories: 'Categories',
  testimonials: 'Testimonials',
  newsletter: 'Newsletter Signup',
};

export const SECTION_TYPE_DEFAULTS: Record<SectionType, Record<string, unknown>> = {
  hero: {
    title: '',
    subtitle: '',
    ctaText: 'Shop Now',
    ctaLink: '/products',
    backgroundImage: '',
    overlayOpacity: 40,
  },
  featured: {
    title: 'Featured Products',
    productCount: 8,
    layout: 'grid',
    showPrice: true,
    showAddToCart: true,
    showRating: true,
  },
  categories: {
    title: 'Shop by Category',
    columns: 4,
    showImages: true,
    showProductCount: true,
    showDescription: false,
  },
  testimonials: {
    title: 'What Our Customers Say',
    items: [],
  },
  newsletter: {
    title: 'Stay Updated',
    subtitle: 'Subscribe to our newsletter for the latest deals and updates.',
    buttonText: 'Subscribe',
    placeholder: 'Enter your email',
  },
};
