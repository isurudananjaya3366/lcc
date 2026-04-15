/**
 * Store Utility Tests — Image Utilities
 */

import {
  getImageUrl,
  getImageSrcSet,
  getPlaceholderImage,
  isValidImageUrl,
  getProductMainImage,
  getProductThumbnail,
} from '@/lib/store/utils/images';

describe('getImageUrl', () => {
  it('returns a CDN URL for a given path', () => {
    const result = getImageUrl('/products/shoe.jpg');
    expect(result).toContain('shoe.jpg');
  });

  it('handles absolute URLs', () => {
    const result = getImageUrl('https://cdn.example.com/img.jpg');
    expect(result).toBe('https://cdn.example.com/img.jpg');
  });
});

describe('getImageSrcSet', () => {
  it('generates srcset with multiple widths', () => {
    const result = getImageSrcSet('/products/shoe.jpg');
    expect(result).toBeTruthy();
    expect(typeof result).toBe('string');
  });
});

describe('getPlaceholderImage', () => {
  it('returns a placeholder image path', () => {
    const result = getPlaceholderImage();
    expect(typeof result).toBe('string');
    expect(result).toBeTruthy();
  });
});

describe('isValidImageUrl', () => {
  it('returns true for valid image URLs', () => {
    expect(isValidImageUrl('https://example.com/img.jpg')).toBe(true);
    expect(isValidImageUrl('https://example.com/img.png')).toBe(true);
  });

  it('returns false for non-image URLs', () => {
    expect(isValidImageUrl('')).toBe(false);
  });
});

describe('getProductMainImage', () => {
  it('returns primary image from product images array', () => {
    const images = [
      { url: '/img1.jpg', is_primary: false, alt_text: '', order: 1 },
      { url: '/img2.jpg', is_primary: true, alt_text: '', order: 0 },
    ];
    const result = getProductMainImage(images);
    expect(result).toBe('/img2.jpg');
  });

  it('returns first image if no primary', () => {
    const images = [{ url: '/img1.jpg', is_primary: false, alt_text: '', order: 0 }];
    const result = getProductMainImage(images);
    expect(result).toBe('/img1.jpg');
  });

  it('returns placeholder for empty array', () => {
    const result = getProductMainImage([]);
    expect(result).toBeTruthy();
  });
});

describe('getProductThumbnail', () => {
  it('returns a thumbnail-sized image URL', () => {
    const images = [{ url: '/img1.jpg', is_primary: true, alt_text: '', order: 0 }];
    const result = getProductThumbnail(images);
    expect(result).toBeTruthy();
  });
});
