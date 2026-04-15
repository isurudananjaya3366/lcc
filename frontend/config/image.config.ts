/**
 * Image Configuration
 *
 * Image sizes, formats, optimization settings, and CDN config.
 */

export interface ImageSize {
  name: string;
  width: number;
  height: number;
  maxFileSize: number; // KB
  quality: number; // 1-100
}

export const imageSizes: ImageSize[] = [
  { name: 'thumbnail', width: 150, height: 150, maxFileSize: 15, quality: 75 },
  { name: 'small', width: 300, height: 300, maxFileSize: 30, quality: 80 },
  { name: 'medium', width: 600, height: 600, maxFileSize: 80, quality: 85 },
  { name: 'large', width: 1200, height: 1200, maxFileSize: 150, quality: 85 },
  { name: 'hero', width: 1920, height: 600, maxFileSize: 200, quality: 80 },
];

export const imageConfig = {
  sizes: imageSizes,

  formats: {
    primary: 'webp' as const,
    fallback: 'jpeg' as const,
    transparency: 'png' as const,
    vector: 'svg' as const,
  },

  cdn: {
    baseUrl: process.env.NEXT_PUBLIC_CDN_URL || '',
    cacheDays: 365,
  },

  upload: {
    maxFileSizeMB: 5,
    minWidth: 800,
    minHeight: 800,
    allowedFormats: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
  },

  lazyLoading: {
    enabled: true,
    rootMargin: '200px',
    threshold: 0.1,
    placeholder: 'blur' as const,
  },

  /** Default placeholder for product images */
  productPlaceholder: '/images/product-placeholder.svg',
  /** Default placeholder for category images */
  categoryPlaceholder: '/images/category-placeholder.svg',
} as const;

/** Get an image size config by name */
export function getImageSize(name: string): ImageSize | undefined {
  return imageSizes.find((s) => s.name === name);
}
