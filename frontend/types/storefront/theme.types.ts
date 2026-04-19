// ================================================================
// Theme Type Definitions
// ================================================================
// TypeScript interfaces for the storefront theme system.
// ================================================================

// ─── Color Types ────────────────────────────────────────────────

export interface ThemeTextColors {
  primary: string;
  secondary: string;
  disabled: string;
}

export interface ThemeBorderColors {
  light: string;
  dark: string;
}

export interface ThemeStatusColors {
  success: string;
  warning: string;
  error: string;
  info: string;
}

export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: ThemeTextColors;
  border: ThemeBorderColors;
  status: ThemeStatusColors;
}

// ─── Font Types ─────────────────────────────────────────────────

export interface ThemeFontWeights {
  light: number;
  normal: number;
  medium: number;
  bold: number;
}

export interface ThemeFonts {
  heading: string;
  body: string;
  scale: number;
  weights: ThemeFontWeights;
}

// ─── Logo Types ─────────────────────────────────────────────────

export interface ThemeLogo {
  url: string;
  alt: string;
  width: number;
  height: number;
  darkModeUrl?: string;
}

// ─── Homepage Types ─────────────────────────────────────────────

export interface ThemeHeroSection {
  title: string;
  subtitle: string;
  ctaText: string;
  ctaLink: string;
  backgroundImage?: string;
  backgroundOverlay?: string;
}

export interface ThemeFeaturedProducts {
  count: number;
  layout: 'grid' | 'carousel';
  title: string;
}

export interface ThemeBanner {
  id: string;
  imageUrl: string;
  altText: string;
  link?: string;
  position: 'top' | 'middle' | 'bottom';
}

export interface ThemeHomepage {
  hero: ThemeHeroSection;
  featuredProducts: ThemeFeaturedProducts;
  banners: ThemeBanner[];
  layout: {
    type: 'standard' | 'minimal' | 'full-width';
    columns: number;
  };
}

// ─── Main Theme Interface ───────────────────────────────────────

export interface Theme {
  id: string;
  tenantId: string;
  name: string;
  colors: ThemeColors;
  fonts: ThemeFonts;
  logo: ThemeLogo;
  homepage: ThemeHomepage;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// ─── Context Types ──────────────────────────────────────────────

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type PartialTheme = DeepPartial<Omit<Theme, 'id' | 'tenantId' | 'createdAt' | 'updatedAt'>>;

export interface ThemeContextValue {
  theme: Theme | null;
  updateTheme: (updates: PartialTheme) => Promise<void>;
  resetTheme: () => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

// ─── Validation Types ───────────────────────────────────────────

export interface ThemeValidationError {
  field: string;
  message: string;
}

export type ThemeValidationResult =
  | { valid: true }
  | { valid: false; errors: ThemeValidationError[] };

// ─── API Types ──────────────────────────────────────────────────

export interface ThemeApiResponse {
  success: boolean;
  data: {
    theme: Theme;
  };
}

export interface ThemeUpdateRequest {
  colors?: Partial<ThemeColors>;
  fonts?: Partial<ThemeFonts>;
  logo?: Partial<ThemeLogo>;
  homepage?: Partial<ThemeHomepage>;
  name?: string;
  isActive?: boolean;
}

// ─── Cache Types ────────────────────────────────────────────────

export interface ThemeCacheEntry {
  theme: Theme;
  timestamp: number;
  version: string;
  tenantId: string;
}

// ─── Store Types ────────────────────────────────────────────────

export interface ThemeStoreState {
  theme: Theme | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  setTheme: (theme: Theme) => void;
  updateTheme: (updates: PartialTheme) => void;
  resetTheme: (defaultTheme: Theme) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// ─── Type Guards ────────────────────────────────────────────────

export function isValidHexColor(value: unknown): value is string {
  return typeof value === 'string' && /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(value);
}

export function isThemeColors(value: unknown): value is ThemeColors {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.primary === 'string' &&
    typeof obj.secondary === 'string' &&
    typeof obj.accent === 'string' &&
    typeof obj.background === 'string' &&
    typeof obj.surface === 'string' &&
    typeof obj.text === 'object' &&
    typeof obj.border === 'object' &&
    typeof obj.status === 'object'
  );
}

export function isThemeFonts(value: unknown): value is ThemeFonts {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.heading === 'string' &&
    typeof obj.body === 'string' &&
    typeof obj.scale === 'number' &&
    typeof obj.weights === 'object'
  );
}
