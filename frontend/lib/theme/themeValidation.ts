// ================================================================
// Theme Validation
// ================================================================
// Validates theme object shape and values.
// ================================================================

import type {
  Theme,
  ThemeColors,
  ThemeFonts,
  ThemeLogo,
  ThemeValidationError,
  ThemeValidationResult,
} from '@/types/storefront/theme.types';
import { isValidHexColor } from '@/types/storefront/theme.types';

// ─── Color Validation ───────────────────────────────────────────

function validateColors(colors: unknown): ThemeValidationError[] {
  const errors: ThemeValidationError[] = [];
  if (typeof colors !== 'object' || colors === null) {
    errors.push({ field: 'colors', message: 'Colors must be an object' });
    return errors;
  }

  const c = colors as Record<string, unknown>;

  const topLevelColorFields = ['primary', 'secondary', 'accent', 'background', 'surface'] as const;
  for (const field of topLevelColorFields) {
    if (!isValidHexColor(c[field])) {
      errors.push({ field: `colors.${field}`, message: `Invalid hex color for ${field}` });
    }
  }

  if (typeof c.text === 'object' && c.text !== null) {
    const text = c.text as Record<string, unknown>;
    for (const field of ['primary', 'secondary', 'disabled'] as const) {
      if (!isValidHexColor(text[field])) {
        errors.push({
          field: `colors.text.${field}`,
          message: `Invalid hex color for text.${field}`,
        });
      }
    }
  } else {
    errors.push({ field: 'colors.text', message: 'Text colors must be an object' });
  }

  if (typeof c.border === 'object' && c.border !== null) {
    const border = c.border as Record<string, unknown>;
    for (const field of ['light', 'dark'] as const) {
      if (!isValidHexColor(border[field])) {
        errors.push({
          field: `colors.border.${field}`,
          message: `Invalid hex color for border.${field}`,
        });
      }
    }
  } else {
    errors.push({ field: 'colors.border', message: 'Border colors must be an object' });
  }

  if (typeof c.status === 'object' && c.status !== null) {
    const status = c.status as Record<string, unknown>;
    for (const field of ['success', 'warning', 'error', 'info'] as const) {
      if (!isValidHexColor(status[field])) {
        errors.push({
          field: `colors.status.${field}`,
          message: `Invalid hex color for status.${field}`,
        });
      }
    }
  } else {
    errors.push({ field: 'colors.status', message: 'Status colors must be an object' });
  }

  return errors;
}

// ─── Font Validation ────────────────────────────────────────────

function validateFonts(fonts: unknown): ThemeValidationError[] {
  const errors: ThemeValidationError[] = [];
  if (typeof fonts !== 'object' || fonts === null) {
    errors.push({ field: 'fonts', message: 'Fonts must be an object' });
    return errors;
  }

  const f = fonts as Record<string, unknown>;

  if (typeof f.heading !== 'string' || !f.heading) {
    errors.push({ field: 'fonts.heading', message: 'Heading font is required' });
  }
  if (typeof f.body !== 'string' || !f.body) {
    errors.push({ field: 'fonts.body', message: 'Body font is required' });
  }
  if (typeof f.scale !== 'number' || f.scale <= 0 || f.scale > 3) {
    errors.push({ field: 'fonts.scale', message: 'Font scale must be between 0 and 3' });
  }

  if (typeof f.weights === 'object' && f.weights !== null) {
    const w = f.weights as Record<string, unknown>;
    for (const field of ['light', 'normal', 'medium', 'bold'] as const) {
      if (typeof w[field] !== 'number' || w[field] < 100 || w[field] > 900) {
        errors.push({
          field: `fonts.weights.${field}`,
          message: `Font weight ${field} must be 100-900`,
        });
      }
    }
  } else {
    errors.push({ field: 'fonts.weights', message: 'Font weights must be an object' });
  }

  return errors;
}

// ─── Logo Validation ────────────────────────────────────────────

function validateLogo(logo: unknown): ThemeValidationError[] {
  const errors: ThemeValidationError[] = [];
  if (typeof logo !== 'object' || logo === null) {
    errors.push({ field: 'logo', message: 'Logo must be an object' });
    return errors;
  }

  const l = logo as Record<string, unknown>;

  if (typeof l.url !== 'string') {
    errors.push({ field: 'logo.url', message: 'Logo URL is required' });
  }
  if (typeof l.alt !== 'string') {
    errors.push({ field: 'logo.alt', message: 'Logo alt text is required' });
  }
  if (typeof l.width !== 'number' || l.width <= 0) {
    errors.push({ field: 'logo.width', message: 'Logo width must be a positive number' });
  }
  if (typeof l.height !== 'number' || l.height <= 0) {
    errors.push({ field: 'logo.height', message: 'Logo height must be a positive number' });
  }

  return errors;
}

// ─── Main Validation ────────────────────────────────────────────

export function validateTheme(theme: unknown): ThemeValidationResult {
  const errors: ThemeValidationError[] = [];

  if (typeof theme !== 'object' || theme === null) {
    return { valid: false, errors: [{ field: 'theme', message: 'Theme must be an object' }] };
  }

  const t = theme as Record<string, unknown>;

  if (typeof t.id !== 'string') {
    errors.push({ field: 'id', message: 'Theme id is required' });
  }
  if (typeof t.name !== 'string') {
    errors.push({ field: 'name', message: 'Theme name is required' });
  }

  errors.push(...validateColors(t.colors));
  errors.push(...validateFonts(t.fonts));
  errors.push(...validateLogo(t.logo));

  if (errors.length > 0) {
    return { valid: false, errors };
  }

  return { valid: true };
}

export function isValidTheme(theme: unknown): theme is Theme {
  return validateTheme(theme).valid;
}
