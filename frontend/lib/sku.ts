/**
 * Generate a random alphanumeric suffix (uppercase + digits).
 */
function generateRandomSuffix(length = 5): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  for (let i = 0; i < length; i++) {
    result += chars[(array[i] ?? 0) % chars.length];
  }
  return result;
}

/**
 * Generate a SKU from a product name.
 *
 * 1. Remove special characters (keep letters, numbers, spaces, dashes)
 * 2. Convert to uppercase
 * 3. Replace spaces with dashes
 * 4. Collapse consecutive dashes
 * 5. Truncate to 20 characters
 * 6. Append a random 5-character suffix
 */
export function generateSKU(name: string): string {
  if (!name || !name.trim()) {
    return generateRandomSuffix(10);
  }

  const base = name
    .replace(/[^a-zA-Z0-9\s-]/g, '')
    .toUpperCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 20);

  if (!base) {
    return generateRandomSuffix(10);
  }

  return `${base}-${generateRandomSuffix(5)}`;
}

/**
 * Validate that a SKU matches the expected format.
 */
export function isValidSKU(sku: string): boolean {
  if (!sku || sku.length < 3 || sku.length > 30) return false;
  return /^[A-Z0-9-]+$/.test(sku);
}
