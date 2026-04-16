/**
 * Logo utility functions for the storefront header.
 */

/**
 * Get the logo source, returning a fallback if none provided.
 */
export function getLogoSource(src?: string): string | null {
  if (src && src.trim().length > 0) return src;
  return null;
}

/**
 * Handle logo image load error by hiding the image.
 */
export function handleLogoError(event: React.SyntheticEvent<HTMLImageElement>): void {
  const img = event.currentTarget;
  img.style.display = 'none';
}

/**
 * Generate a text-based placeholder for the store logo.
 */
export function getLogoPlaceholder(storeName: string): {
  primary: string;
  secondary: string;
} {
  const parts = storeName.split(/\s+/);
  if (parts.length >= 2) {
    return {
      primary: parts[0],
      secondary: parts.slice(1).join(' '),
    };
  }
  return { primary: storeName, secondary: '' };
}
