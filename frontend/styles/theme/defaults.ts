// ================================================================
// Default Theme Configuration
// ================================================================
// LankaCommerce Cloud default brand theme.
// Used as fallback when no custom theme is loaded.
// ================================================================

import type {
  Theme,
  ThemeColors,
  ThemeFonts,
  ThemeLogo,
  ThemeHomepage,
} from '@/types/storefront/theme.types';

// ─── Default Colors ─────────────────────────────────────────────

export const defaultColors: ThemeColors = {
  primary: '#2563eb',
  secondary: '#64748b',
  accent: '#f59e0b',
  background: '#ffffff',
  surface: '#f8fafc',
  text: {
    primary: '#0f172a',
    secondary: '#64748b',
    disabled: '#cbd5e1',
  },
  border: {
    light: '#e2e8f0',
    dark: '#94a3b8',
  },
  status: {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },
};

// ─── Default Fonts ──────────────────────────────────────────────

export const defaultFonts: ThemeFonts = {
  heading: 'Inter, system-ui, sans-serif',
  body: 'Open Sans, system-ui, sans-serif',
  scale: 1.0,
  weights: {
    light: 300,
    normal: 400,
    medium: 500,
    bold: 700,
  },
};

// ─── Default Logo ───────────────────────────────────────────────

export const defaultLogo: ThemeLogo = {
  url: '/images/default-logo.png',
  alt: 'Store Logo',
  width: 200,
  height: 60,
  darkModeUrl: '/images/default-logo-dark.png',
};

// ─── Default Homepage ───────────────────────────────────────────

export const defaultHomepage: ThemeHomepage = {
  hero: {
    title: 'Welcome to Our Store',
    subtitle: 'Discover amazing products at great prices',
    ctaText: 'Shop Now',
    ctaLink: '/products',
    backgroundOverlay: 'rgba(0, 0, 0, 0.4)',
  },
  featuredProducts: {
    count: 8,
    layout: 'grid',
    title: 'Featured Products',
  },
  banners: [],
  layout: {
    type: 'standard',
    columns: 4,
  },
};

// ─── Complete Default Theme ─────────────────────────────────────

export const defaultTheme: Theme = {
  id: 'default',
  tenantId: '',
  name: 'LankaCommerce Default',
  colors: defaultColors,
  fonts: defaultFonts,
  logo: defaultLogo,
  homepage: defaultHomepage,
  isActive: true,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};
