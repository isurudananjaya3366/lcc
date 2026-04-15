/**
 * URL Utilities
 *
 * Product and category URL generators, slug helpers, breadcrumb builders,
 * and canonical URL generators for the storefront.
 */

// ─── Product URLs ────────────────────────────────────────────────────────────

/**
 * Get the URL for a single product page.
 * @example getProductUrl('blue-sneakers') → "/products/blue-sneakers"
 */
export function getProductUrl(slug: string): string {
  return `/products/${encodeURIComponent(slug)}`;
}

/**
 * Get the products listing URL with optional filters.
 * @example getProductsUrl({ category: 'shoes', sort: 'price_asc' }) → "/products?category=shoes&sort=price_asc"
 */
export function getProductsUrl(
  filters?: Record<string, string | number | boolean | undefined>
): string {
  if (!filters) return '/products';

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value));
    }
  }

  const qs = params.toString();
  return qs ? `/products?${qs}` : '/products';
}

/**
 * Get the canonical URL for a product (absolute).
 */
export function getCanonicalProductUrl(slug: string): string {
  const base = process.env.NEXT_PUBLIC_STORE_URL || 'http://localhost:3000';
  return `${base}/products/${encodeURIComponent(slug)}`;
}

/**
 * Get the URL for a specific product variant.
 * @example getProductVariantUrl('blue-sneakers', 'size-42') → "/products/blue-sneakers?variant=size-42"
 */
export function getProductVariantUrl(slug: string, variantId: string): string {
  return `/products/${encodeURIComponent(slug)}?variant=${encodeURIComponent(variantId)}`;
}

/**
 * Parse a product URL to extract slug and optional variant.
 */
export function parseProductUrl(url: string): { slug: string; variant?: string } | null {
  const match = url.match(/\/products\/([^/?#]+)/);
  if (!match) return null;

  const slug = decodeURIComponent(match[1]!);
  const urlObj = safeParseUrl(url);
  const variant = urlObj?.searchParams.get('variant') || undefined;

  return { slug, variant };
}

// ─── Category URLs ───────────────────────────────────────────────────────────

/** Category node with optional parent reference for hierarchy traversal. */
export interface CategoryNode {
  slug: string;
  name: string;
  parentSlug?: string;
  parent?: CategoryNode;
  children?: CategoryNode[];
}

/**
 * Get the path segments from root to the given category.
 * Traverses `parent` references to build [grandparent, parent, child].
 */
export function getCategoryPath(category: CategoryNode): string[] {
  const segments: string[] = [];
  let current: CategoryNode | undefined = category;
  while (current) {
    segments.unshift(current.slug);
    current = current.parent;
  }
  return segments;
}

/**
 * Get the depth (0-based) of a category in its hierarchy.
 */
export function getCategoryDepth(category: CategoryNode): number {
  let depth = 0;
  let current = category.parent;
  while (current) {
    depth++;
    current = current.parent;
  }
  return depth;
}

/**
 * Get the URL for a category page.
 * Accepts a slug string (flat) or a CategoryNode (hierarchical).
 * @example getCategoryUrl('electronics') → "/categories/electronics"
 * @example getCategoryUrl(node) → "/categories/electronics/laptops"
 */
export function getCategoryUrl(slugOrCategory: string | CategoryNode): string {
  if (typeof slugOrCategory === 'string') {
    return `/categories/${encodeURIComponent(slugOrCategory)}`;
  }
  const segments = getCategoryPath(slugOrCategory);
  return `/categories/${segments.map(encodeURIComponent).join('/')}`;
}

/**
 * Get the URL for a category's product listing with filters.
 */
export function getCategoryProductsUrl(
  slug: string,
  filters?: Record<string, string | number | undefined>
): string {
  const base = `/categories/${encodeURIComponent(slug)}`;
  if (!filters) return base;

  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value));
    }
  }

  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

/**
 * Get the categories listing URL with optional filters.
 */
export function getCategoriesUrl(
  filters?: { level?: number; parent?: string; sort?: string }
): string {
  if (!filters) return '/categories';

  const params = new URLSearchParams();
  if (filters.level !== undefined) params.set('level', String(filters.level));
  if (filters.parent) params.set('parent', filters.parent);
  if (filters.sort) params.set('sort', filters.sort);

  const qs = params.toString();
  return qs ? `/categories?${qs}` : '/categories';
}

/**
 * Get the canonical URL for a category (absolute).
 */
export function getCanonicalCategoryUrl(slug: string): string {
  const base = process.env.NEXT_PUBLIC_STORE_URL || 'http://localhost:3000';
  return `${base}/categories/${encodeURIComponent(slug)}`;
}

/**
 * Parse a category URL to extract slug(s).
 */
export function parseCategoryUrl(url: string): { slug: string; slugs: string[] } | null {
  const match = url.match(/\/categories\/([^?#]+)/);
  if (!match) return null;
  const slugs = match[1]!.split('/').map(decodeURIComponent);
  return { slug: slugs[slugs.length - 1]!, slugs };
}

/**
 * Get the parent category's URL. Returns null for root categories.
 */
export function getParentCategoryUrl(category: CategoryNode): string | null {
  if (!category.parent) return null;
  return getCategoryUrl(category.parent);
}

/**
 * Get the URL showing child categories of a given category.
 */
export function getChildCategoriesUrl(category: CategoryNode): string {
  return getCategoriesUrl({ parent: category.slug });
}

/**
 * Get the URL showing sibling categories (same parent).
 */
export function getSiblingCategoriesUrl(category: CategoryNode): string {
  if (!category.parent) return getCategoriesUrl({ level: 0 });
  return getCategoriesUrl({ parent: category.parent.slug });
}

/**
 * Extract the category path segments from a URL string.
 * @example getCategoryPathFromUrl('/categories/electronics/laptops') → ['electronics', 'laptops']
 */
export function getCategoryPathFromUrl(url: string): string[] {
  const parsed = parseCategoryUrl(url);
  return parsed ? parsed.slugs : [];
}

/**
 * Validate that a URL is a well-formed category URL.
 */
export function isValidCategoryUrl(url: string): boolean {
  return /\/categories\/[a-z0-9][a-z0-9-]*(\/[a-z0-9][a-z0-9-]*)*$/.test(url.split('?')[0]!);
}

/**
 * Generate a slug for a category, optionally scoped to a parent.
 */
export function generateCategorySlug(name: string, parent?: CategoryNode): string {
  const base = generateSlug(name);
  return parent ? `${parent.slug}-${base}` : base;
}

/** Check if `child` is a direct child of `parent`. */
export function isChildOf(child: CategoryNode, parent: CategoryNode): boolean {
  return child.parent?.slug === parent.slug;
}

/** Check if `descendant` is a descendant of `ancestor` (any depth). */
export function isDescendantOf(descendant: CategoryNode, ancestor: CategoryNode): boolean {
  let current = descendant.parent;
  while (current) {
    if (current.slug === ancestor.slug) return true;
    current = current.parent;
  }
  return false;
}

// ─── Breadcrumbs ─────────────────────────────────────────────────────────────

export interface BreadcrumbItem {
  label: string;
  href: string;
}

/**
 * Generate breadcrumbs for a category hierarchy.
 * Accepts a pre-built array of {name, slug} or a CategoryNode (traverses parent chain).
 */
export function getBreadcrumbs(
  input: Array<{ name: string; slug: string }> | CategoryNode
): BreadcrumbItem[] {
  const crumbs: BreadcrumbItem[] = [{ label: 'Home', href: '/' }];

  if (Array.isArray(input)) {
    for (const cat of input) {
      crumbs.push({ label: cat.name, href: getCategoryUrl(cat.slug) });
    }
  } else {
    // Traverse parent chain to build hierarchy
    const chain: CategoryNode[] = [];
    let current: CategoryNode | undefined = input;
    while (current) {
      chain.unshift(current);
      current = current.parent;
    }
    for (const cat of chain) {
      crumbs.push({ label: cat.name, href: getCategoryUrl(cat.slug) });
    }
  }

  return crumbs;
}

// ─── Slug Helpers ────────────────────────────────────────────────────────────

/**
 * Generate a URL-safe slug from a string.
 * @example generateSlug('Blue Running Shoes (Size 42)') → "blue-running-shoes-size-42"
 */
export function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // Remove special chars
    .replace(/[\s_]+/g, '-') // Replace spaces/underscores with hyphens
    .replace(/-+/g, '-') // Collapse multiple hyphens
    .replace(/^-|-$/g, ''); // Trim leading/trailing hyphens
}

// ─── Other Store URLs ────────────────────────────────────────────────────────

export function getCartUrl(): string {
  return '/cart';
}

export function getCheckoutUrl(): string {
  return '/checkout';
}

export function getAccountUrl(): string {
  return '/account';
}

export function getOrderUrl(orderNumber: string): string {
  return `/account/orders/${encodeURIComponent(orderNumber)}`;
}

export function getSearchUrl(query: string): string {
  return `/search?q=${encodeURIComponent(query)}`;
}

// ─── Internal ────────────────────────────────────────────────────────────────

function safeParseUrl(url: string): URL | null {
  try {
    // Handle relative URLs
    const base = 'http://localhost';
    return new URL(url, base);
  } catch {
    return null;
  }
}
