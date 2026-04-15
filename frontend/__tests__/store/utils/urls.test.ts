/**
 * Store Utility Tests — URL Utilities (Product + Category)
 */

import {
  getProductUrl,
  getProductsUrl,
  getCanonicalProductUrl,
  getProductVariantUrl,
  parseProductUrl,
  getCategoryUrl,
  getCategoryProductsUrl,
  getCategoriesUrl,
  getCanonicalCategoryUrl,
  parseCategoryUrl,
  getParentCategoryUrl,
  getChildCategoriesUrl,
  getSiblingCategoriesUrl,
  getCategoryPathFromUrl,
  isValidCategoryUrl,
  generateCategorySlug,
  isChildOf,
  isDescendantOf,
  getCategoryDepth,
  getCategoryPath,
  getBreadcrumbs,
  generateSlug,
  getCartUrl,
  getCheckoutUrl,
  getAccountUrl,
  getSearchUrl,
  type CategoryNode,
} from '@/lib/store/utils/urls';

// ── Product URLs ──────────────────────────────────────────────

describe('getProductUrl', () => {
  it('generates a product URL from slug', () => {
    expect(getProductUrl('blue-sneakers')).toBe('/products/blue-sneakers');
  });

  it('encodes special characters', () => {
    expect(getProductUrl('a b')).toBe('/products/a%20b');
  });
});

describe('getProductsUrl', () => {
  it('returns /products with no filters', () => {
    expect(getProductsUrl()).toBe('/products');
  });

  it('adds query params for filters', () => {
    const url = getProductsUrl({ category: 'shoes', sort: 'price_asc' });
    expect(url).toContain('category=shoes');
    expect(url).toContain('sort=price_asc');
  });

  it('skips undefined values', () => {
    const url = getProductsUrl({ category: undefined, sort: 'newest' });
    expect(url).not.toContain('category');
    expect(url).toContain('sort=newest');
  });
});

describe('getCanonicalProductUrl', () => {
  it('returns an absolute URL', () => {
    const url = getCanonicalProductUrl('test-product');
    expect(url).toMatch(/^https?:\/\//);
    expect(url).toContain('/products/test-product');
  });
});

describe('getProductVariantUrl', () => {
  it('adds variant query param', () => {
    expect(getProductVariantUrl('shoe', 'size-42')).toBe('/products/shoe?variant=size-42');
  });
});

describe('parseProductUrl', () => {
  it('extracts slug from product URL', () => {
    const result = parseProductUrl('/products/blue-sneakers');
    expect(result).toEqual({ slug: 'blue-sneakers', variant: undefined });
  });

  it('extracts slug and variant', () => {
    const result = parseProductUrl('/products/blue-sneakers?variant=size-42');
    expect(result?.slug).toBe('blue-sneakers');
    expect(result?.variant).toBe('size-42');
  });

  it('returns null for non-product URL', () => {
    expect(parseProductUrl('/categories/electronics')).toBeNull();
  });
});

// ── Category URLs ─────────────────────────────────────────────

describe('getCategoryUrl', () => {
  it('generates a category URL from string slug', () => {
    expect(getCategoryUrl('electronics')).toBe('/categories/electronics');
  });

  it('generates hierarchical URL from CategoryNode', () => {
    const parent: CategoryNode = { slug: 'electronics', name: 'Electronics' };
    const child: CategoryNode = { slug: 'laptops', name: 'Laptops', parent };
    expect(getCategoryUrl(child)).toBe('/categories/electronics/laptops');
  });
});

describe('getCategoriesUrl', () => {
  it('returns /categories with no filters', () => {
    expect(getCategoriesUrl()).toBe('/categories');
  });

  it('adds level filter', () => {
    expect(getCategoriesUrl({ level: 0 })).toContain('level=0');
  });

  it('adds parent filter', () => {
    expect(getCategoriesUrl({ parent: 'electronics' })).toContain('parent=electronics');
  });
});

describe('parseCategoryUrl', () => {
  it('extracts slug from flat category URL', () => {
    const result = parseCategoryUrl('/categories/electronics');
    expect(result?.slug).toBe('electronics');
    expect(result?.slugs).toEqual(['electronics']);
  });

  it('extracts hierarchical slugs', () => {
    const result = parseCategoryUrl('/categories/electronics/laptops');
    expect(result?.slugs).toEqual(['electronics', 'laptops']);
    expect(result?.slug).toBe('laptops');
  });

  it('returns null for non-category URL', () => {
    expect(parseCategoryUrl('/products/test')).toBeNull();
  });
});

describe('getCategoryPath', () => {
  it('returns path from root to leaf', () => {
    const root: CategoryNode = { slug: 'electronics', name: 'Electronics' };
    const mid: CategoryNode = { slug: 'computers', name: 'Computers', parent: root };
    const leaf: CategoryNode = { slug: 'laptops', name: 'Laptops', parent: mid };
    expect(getCategoryPath(leaf)).toEqual(['electronics', 'computers', 'laptops']);
  });

  it('returns single slug for root category', () => {
    const root: CategoryNode = { slug: 'electronics', name: 'Electronics' };
    expect(getCategoryPath(root)).toEqual(['electronics']);
  });
});

describe('getCategoryDepth', () => {
  it('returns 0 for root', () => {
    const root: CategoryNode = { slug: 'root', name: 'Root' };
    expect(getCategoryDepth(root)).toBe(0);
  });

  it('returns correct depth for nested', () => {
    const root: CategoryNode = { slug: 'root', name: 'Root' };
    const child: CategoryNode = { slug: 'child', name: 'Child', parent: root };
    const grandchild: CategoryNode = { slug: 'gc', name: 'GC', parent: child };
    expect(getCategoryDepth(grandchild)).toBe(2);
  });
});

describe('getParentCategoryUrl', () => {
  it('returns null for root category', () => {
    const root: CategoryNode = { slug: 'root', name: 'Root' };
    expect(getParentCategoryUrl(root)).toBeNull();
  });

  it('returns parent URL for child', () => {
    const parent: CategoryNode = { slug: 'electronics', name: 'Electronics' };
    const child: CategoryNode = { slug: 'laptops', name: 'Laptops', parent };
    expect(getParentCategoryUrl(child)).toBe('/categories/electronics');
  });
});

describe('isChildOf / isDescendantOf', () => {
  const root: CategoryNode = { slug: 'root', name: 'Root' };
  const child: CategoryNode = { slug: 'child', name: 'Child', parent: root };
  const grandchild: CategoryNode = { slug: 'gc', name: 'GC', parent: child };

  it('isChildOf returns true for direct child', () => {
    expect(isChildOf(child, root)).toBe(true);
  });

  it('isChildOf returns false for grandchild', () => {
    expect(isChildOf(grandchild, root)).toBe(false);
  });

  it('isDescendantOf returns true for grandchild', () => {
    expect(isDescendantOf(grandchild, root)).toBe(true);
  });

  it('isDescendantOf returns false for unrelated', () => {
    const other: CategoryNode = { slug: 'other', name: 'Other' };
    expect(isDescendantOf(grandchild, other)).toBe(false);
  });
});

describe('isValidCategoryUrl', () => {
  it('returns true for valid URLs', () => {
    expect(isValidCategoryUrl('/categories/electronics')).toBe(true);
    expect(isValidCategoryUrl('/categories/electronics/laptops')).toBe(true);
  });

  it('returns false for invalid URLs', () => {
    expect(isValidCategoryUrl('/products/test')).toBe(false);
  });
});

describe('generateCategorySlug', () => {
  it('generates slug from name', () => {
    expect(generateCategorySlug('Gaming Laptops')).toBe('gaming-laptops');
  });

  it('scopes to parent', () => {
    const parent: CategoryNode = { slug: 'electronics', name: 'Electronics' };
    expect(generateCategorySlug('Laptops', parent)).toBe('electronics-laptops');
  });
});

describe('getCategoryPathFromUrl', () => {
  it('extracts path segments', () => {
    expect(getCategoryPathFromUrl('/categories/a/b/c')).toEqual(['a', 'b', 'c']);
  });

  it('returns empty for non-category URL', () => {
    expect(getCategoryPathFromUrl('/products/test')).toEqual([]);
  });
});

// ── Breadcrumbs ───────────────────────────────────────────────

describe('getBreadcrumbs', () => {
  it('builds from array of {name, slug}', () => {
    const result = getBreadcrumbs([
      { name: 'Electronics', slug: 'electronics' },
      { name: 'Laptops', slug: 'laptops' },
    ]);
    expect(result[0]).toEqual({ label: 'Home', href: '/' });
    expect(result[1]).toEqual({ label: 'Electronics', href: '/categories/electronics' });
    expect(result[2]).toEqual({ label: 'Laptops', href: '/categories/laptops' });
  });

  it('builds from CategoryNode (parent chain)', () => {
    const parent: CategoryNode = { slug: 'electronics', name: 'Electronics' };
    const child: CategoryNode = { slug: 'laptops', name: 'Laptops', parent };
    const result = getBreadcrumbs(child);
    expect(result).toHaveLength(3); // Home + Electronics + Laptops
    expect(result[0]?.label).toBe('Home');
    expect(result[1]?.label).toBe('Electronics');
    expect(result[2]?.label).toBe('Laptops');
  });
});

// ── Slugs ─────────────────────────────────────────────────────

describe('generateSlug', () => {
  it('converts text to URL-safe slug', () => {
    expect(generateSlug('Blue Running Shoes (Size 42)')).toBe('blue-running-shoes-size-42');
  });

  it('handles multiple spaces', () => {
    expect(generateSlug('  a   b  ')).toBe('a-b');
  });
});

// ── Other URLs ────────────────────────────────────────────────

describe('store routes', () => {
  it('getCartUrl', () => expect(getCartUrl()).toBe('/cart'));
  it('getCheckoutUrl', () => expect(getCheckoutUrl()).toBe('/checkout'));
  it('getAccountUrl', () => expect(getAccountUrl()).toBe('/account'));
  it('getSearchUrl', () => expect(getSearchUrl('shoes')).toBe('/search?q=shoes'));
});
