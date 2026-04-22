/**
 * Image URL Utilities
 *
 * Helpers for generating image URLs, srcsets, placeholders, and CDN paths
 * for the storefront product catalog.
 */

// ─── Types ───────────────────────────────────────────────────────────────────

export type ImageSize = 'thumbnail' | 'small' | 'medium' | 'large' | 'hero';

interface ImageDimensions {
  width: number;
  height: number;
}

const IMAGE_SIZES: Record<ImageSize, ImageDimensions> = {
  thumbnail: { width: 150, height: 150 },
  small: { width: 300, height: 300 },
  medium: { width: 600, height: 600 },
  large: { width: 1200, height: 1200 },
  hero: { width: 1920, height: 600 },
};

const PLACEHOLDER_IMAGE = '/images/placeholder-product.svg';

function getCdnBase(): string {
  return process.env.NEXT_PUBLIC_CDN_URL || '';
}

// ─── Core ────────────────────────────────────────────────────────────────────

/**
 * Get a resized image URL via CDN or path convention.
 * @example getImageUrl('/uploads/shoe.jpg', 'medium') → "https://cdn.example.com/uploads/shoe.jpg?w=600&h=600&f=webp"
 */
export function getImageUrl(path: string | undefined | null, size: ImageSize = 'medium'): string {
  if (!path) return PLACEHOLDER_IMAGE;

  const cdnBase = getCdnBase();
  const dims = IMAGE_SIZES[size];

  if (cdnBase) {
    const separator = path.includes('?') ? '&' : '?';
    return `${cdnBase}${path}${separator}w=${dims.width}&h=${dims.height}&f=webp`;
  }

  return path;
}

/**
 * Generate a srcSet for responsive images.
 * @example getImageSrcSet('/uploads/shoe.jpg') → "...150w, ...300w, ...600w, ...1200w"
 */
export function getImageSrcSet(
  path: string | undefined | null,
  sizes: ImageSize[] = ['thumbnail', 'small', 'medium', 'large']
): string {
  if (!path) return '';

  return sizes
    .map((size) => {
      const url = getImageUrl(path, size);
      const dims = IMAGE_SIZES[size];
      return `${url} ${dims.width}w`;
    })
    .join(', ');
}

/**
 * Get the placeholder image URL.
 */
export function getPlaceholderImage(): string {
  return PLACEHOLDER_IMAGE;
}

/**
 * Optimize an image URL with query parameters.
 */
export function optimizeImageUrl(
  url: string,
  options?: {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'jpeg' | 'png';
  }
): string {
  if (!url) return PLACEHOLDER_IMAGE;

  const params = new URLSearchParams();
  if (options?.width) params.set('w', String(options.width));
  if (options?.height) params.set('h', String(options.height));
  if (options?.quality) params.set('q', String(options.quality));
  if (options?.format) params.set('f', options.format);

  const paramStr = params.toString();
  if (!paramStr) return url;

  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}${paramStr}`;
}

/**
 * Validate whether a string looks like a valid image URL.
 */
export function isValidImageUrl(url: string): boolean {
  if (!url) return false;
  const imageExtensions = /\.(jpg|jpeg|png|gif|webp|svg|avif)(\?.*)?$/i;
  try {
    // Check if it's a relative path with image extension
    if (url.startsWith('/') || url.startsWith('.')) return imageExtensions.test(url);
    // Check if it's an absolute URL
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// ─── Product Image Helpers ───────────────────────────────────────────────────

interface ProductImageData {
  url: string;
  altText?: string;
  alt_text?: string;
  isPrimary?: boolean;
  is_primary?: boolean;
}

/**
 * Get the main product image (primary or first).
 */
export function getProductMainImage(
  images: ProductImageData[] | undefined,
  size: ImageSize = 'medium'
): string {
  if (!images || images.length === 0) return PLACEHOLDER_IMAGE;
  const primary = images.find((img) => img.isPrimary || img.is_primary) ?? images[0];
  return getImageUrl(primary!.url, size);
}

/**
 * Get all product gallery images.
 */
export function getProductGallery(
  images: ProductImageData[] | undefined,
  size: ImageSize = 'large'
): string[] {
  if (!images || images.length === 0) return [PLACEHOLDER_IMAGE];
  return images.map((img) => getImageUrl(img.url, size));
}

/**
 * Get a product thumbnail.
 */
export function getProductThumbnail(images: ProductImageData[] | undefined): string {
  return getProductMainImage(images, 'thumbnail');
}
