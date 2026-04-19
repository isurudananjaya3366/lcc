/**
 * Responsive srcSet generation utilities.
 */

export interface SrcSetOptions {
  src: string;
  widths?: number[];
  densities?: number[];
  quality?: number;
}

const DEFAULT_WIDTHS = [320, 640, 768, 1024, 1280, 1920];
const DEFAULT_DENSITIES = [1, 2, 3];

/** Generate width-based srcSet string */
export function generateWidthSrcSet(options: SrcSetOptions): string {
  const { src, widths = DEFAULT_WIDTHS, quality = 75 } = options;

  return widths
    .map((w) => `${buildImageUrl(src, w, quality)} ${w}w`)
    .join(', ');
}

/** Generate density-based srcSet string (1x, 2x, 3x) */
export function generateDensitySrcSet(
  options: SrcSetOptions & { baseWidth: number }
): string {
  const { src, densities = DEFAULT_DENSITIES, baseWidth, quality = 75 } = options;

  return densities
    .map((d) => `${buildImageUrl(src, baseWidth * d, quality)} ${d}x`)
    .join(', ');
}

function buildImageUrl(src: string, width: number, quality: number): string {
  if (src.startsWith('http')) return src;
  return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality}`;
}

/** Predefined sizes attributes for common layouts */
export const SIZES_PRESETS = {
  grid: '(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, 25vw',
  hero: '100vw',
  thumbnail: '100px',
  productDetail: '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 600px',
  halfWidth: '(max-width: 768px) 100vw, 50vw',
} as const;
