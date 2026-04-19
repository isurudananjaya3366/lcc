/**
 * Image Size Presets & Performance Configuration
 *
 * Centralized responsive image sizing for product, thumbnail, hero, and background images.
 */

// ── Product Image Sizes ─────────────────────────────────────────

export const PRODUCT_IMAGE_SIZES = {
  card: { width: 300, height: 300, sizes: '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 300px' },
  detail: { width: 600, height: 600, sizes: '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 600px' },
  thumbnail: { width: 100, height: 100, sizes: '100px' },
  miniCart: { width: 80, height: 80, sizes: '80px' },
} as const;

// ── Thumbnail Sizes ─────────────────────────────────────────────

export const THUMBNAIL_SIZES = {
  small: { width: 50, height: 50, sizes: '50px' },
  medium: { width: 100, height: 100, sizes: '100px' },
  large: { width: 150, height: 150, sizes: '150px' },
} as const;

// ── Hero Image Config ────────────────────────────────────────────

export const HERO_IMAGE_CONFIG = {
  desktop: { width: 1920, height: 600, sizes: '100vw' },
  tablet: { width: 1024, height: 400, sizes: '100vw' },
  mobile: { width: 640, height: 300, sizes: '100vw' },
  aspectRatio: '16/5' as const,
  priority: true,
} as const;

// ── Background Image Config ─────────────────────────────────────

export const BACKGROUND_IMAGE_CONFIG = {
  overlay: 'bg-black/40',
  zIndex: {
    background: -1,
    overlay: 0,
    content: 1,
  },
  position: 'object-cover object-center',
} as const;

// ── srcSet Presets ──────────────────────────────────────────────

export const SIZES_PRESETS = {
  grid: '(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw',
  hero: '100vw',
  thumbnail: '100px',
  fullWidth: '100vw',
  halfWidth: '(max-width: 768px) 100vw, 50vw',
} as const;
