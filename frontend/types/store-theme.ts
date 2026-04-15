/** Store theme modes */
export type StoreTheme = 'light' | 'dark' | 'auto';

/** Store theme context value exposed via useStoreTheme */
export interface StoreThemeContextValue {
  theme: StoreTheme;
  setTheme: (theme: StoreTheme) => void;
  toggleTheme: () => void;
  isDark: boolean;
  isLight: boolean;
}

/** Light and dark color schemes */
export interface StoreThemeColors {
  background: string;
  surface: string;
  textPrimary: string;
  textSecondary: string;
  primary: string;
  accent: string;
  border: string;
  error: string;
  success: string;
}

/** Theme configuration object */
export interface StoreThemeConfig {
  mode: StoreTheme;
  colors: StoreThemeColors;
}
