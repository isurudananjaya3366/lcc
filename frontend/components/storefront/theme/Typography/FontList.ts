// ================================================================
// Font List – Available Google Fonts
// ================================================================
// Curated list of popular Google Fonts with metadata for the
// theme typography selector.
// ================================================================

export type FontCategory = 'sans-serif' | 'serif' | 'display' | 'monospace';

export interface FontDefinition {
  id: string;
  name: string;
  family: string;
  category: FontCategory;
  weights: number[];
  hasItalic: boolean;
  popularity: number;
  recommended: boolean;
  pairsWith: string[];
}

// ─── Sans-Serif ─────────────────────────────────────────────────

const sansSerifFonts: FontDefinition[] = [
  {
    id: 'inter',
    name: 'Inter',
    family: "'Inter', sans-serif",
    category: 'sans-serif',
    weights: [400, 500, 600, 700, 800],
    hasItalic: true,
    popularity: 95,
    recommended: true,
    pairsWith: ['merriweather', 'lora', 'playfair-display'],
  },
  {
    id: 'roboto',
    name: 'Roboto',
    family: "'Roboto', sans-serif",
    category: 'sans-serif',
    weights: [300, 400, 500, 700, 900],
    hasItalic: true,
    popularity: 98,
    recommended: true,
    pairsWith: ['roboto-slab', 'merriweather', 'lora'],
  },
  {
    id: 'open-sans',
    name: 'Open Sans',
    family: "'Open Sans', sans-serif",
    category: 'sans-serif',
    weights: [300, 400, 500, 600, 700, 800],
    hasItalic: true,
    popularity: 97,
    recommended: true,
    pairsWith: ['playfair-display', 'lora'],
  },
  {
    id: 'lato',
    name: 'Lato',
    family: "'Lato', sans-serif",
    category: 'sans-serif',
    weights: [300, 400, 700, 900],
    hasItalic: true,
    popularity: 90,
    recommended: true,
    pairsWith: ['merriweather', 'crimson-text'],
  },
  {
    id: 'poppins',
    name: 'Poppins',
    family: "'Poppins', sans-serif",
    category: 'sans-serif',
    weights: [400, 500, 600, 700],
    hasItalic: true,
    popularity: 92,
    recommended: true,
    pairsWith: ['open-sans', 'nunito', 'lora'],
  },
  {
    id: 'montserrat',
    name: 'Montserrat',
    family: "'Montserrat', sans-serif",
    category: 'sans-serif',
    weights: [400, 500, 600, 700, 800],
    hasItalic: true,
    popularity: 91,
    recommended: false,
    pairsWith: ['merriweather', 'lora', 'open-sans'],
  },
  {
    id: 'nunito',
    name: 'Nunito',
    family: "'Nunito', sans-serif",
    category: 'sans-serif',
    weights: [400, 500, 600, 700, 800],
    hasItalic: true,
    popularity: 80,
    recommended: true,
    pairsWith: ['merriweather', 'crimson-text'],
  },
  {
    id: 'source-sans-pro',
    name: 'Source Sans 3',
    family: "'Source Sans 3', sans-serif",
    category: 'sans-serif',
    weights: [400, 500, 600, 700],
    hasItalic: true,
    popularity: 78,
    recommended: true,
    pairsWith: ['source-serif-pro', 'merriweather'],
  },
];

// ─── Serif ──────────────────────────────────────────────────────

const serifFonts: FontDefinition[] = [
  {
    id: 'merriweather',
    name: 'Merriweather',
    family: "'Merriweather', serif",
    category: 'serif',
    weights: [400, 700, 900],
    hasItalic: true,
    popularity: 85,
    recommended: true,
    pairsWith: ['inter', 'roboto', 'open-sans'],
  },
  {
    id: 'lora',
    name: 'Lora',
    family: "'Lora', serif",
    category: 'serif',
    weights: [400, 500, 600, 700],
    hasItalic: true,
    popularity: 82,
    recommended: true,
    pairsWith: ['inter', 'poppins', 'open-sans'],
  },
  {
    id: 'playfair-display',
    name: 'Playfair Display',
    family: "'Playfair Display', serif",
    category: 'serif',
    weights: [400, 500, 600, 700, 800],
    hasItalic: true,
    popularity: 84,
    recommended: false,
    pairsWith: ['open-sans', 'lato', 'source-sans-pro'],
  },
  {
    id: 'crimson-text',
    name: 'Crimson Text',
    family: "'Crimson Text', serif",
    category: 'serif',
    weights: [400, 600, 700],
    hasItalic: true,
    popularity: 65,
    recommended: true,
    pairsWith: ['nunito', 'lato', 'open-sans'],
  },
  {
    id: 'pt-serif',
    name: 'PT Serif',
    family: "'PT Serif', serif",
    category: 'serif',
    weights: [400, 700],
    hasItalic: true,
    popularity: 70,
    recommended: true,
    pairsWith: ['roboto', 'open-sans'],
  },
];

// ─── Display ────────────────────────────────────────────────────

const displayFonts: FontDefinition[] = [
  {
    id: 'bebas-neue',
    name: 'Bebas Neue',
    family: "'Bebas Neue', sans-serif",
    category: 'display',
    weights: [400],
    hasItalic: false,
    popularity: 75,
    recommended: false,
    pairsWith: ['roboto', 'open-sans', 'source-sans-pro'],
  },
  {
    id: 'oswald',
    name: 'Oswald',
    family: "'Oswald', sans-serif",
    category: 'display',
    weights: [400, 500, 600, 700],
    hasItalic: false,
    popularity: 80,
    recommended: false,
    pairsWith: ['open-sans', 'lato', 'roboto'],
  },
  {
    id: 'righteous',
    name: 'Righteous',
    family: "'Righteous', sans-serif",
    category: 'display',
    weights: [400],
    hasItalic: false,
    popularity: 55,
    recommended: false,
    pairsWith: ['roboto', 'open-sans'],
  },
];

// ─── Monospace ──────────────────────────────────────────────────

const monospaceFonts: FontDefinition[] = [
  {
    id: 'roboto-mono',
    name: 'Roboto Mono',
    family: "'Roboto Mono', monospace",
    category: 'monospace',
    weights: [400, 500, 700],
    hasItalic: true,
    popularity: 72,
    recommended: false,
    pairsWith: ['roboto', 'inter'],
  },
  {
    id: 'source-code-pro',
    name: 'Source Code Pro',
    family: "'Source Code Pro', monospace",
    category: 'monospace',
    weights: [400, 500, 600, 700],
    hasItalic: true,
    popularity: 68,
    recommended: false,
    pairsWith: ['source-sans-pro', 'inter'],
  },
  {
    id: 'fira-code',
    name: 'Fira Code',
    family: "'Fira Code', monospace",
    category: 'monospace',
    weights: [400, 500, 600, 700],
    hasItalic: false,
    popularity: 70,
    recommended: false,
    pairsWith: ['inter', 'roboto'],
  },
];

// ─── Combined Exports ───────────────────────────────────────────

export const fontList: FontDefinition[] = [
  ...sansSerifFonts,
  ...serifFonts,
  ...displayFonts,
  ...monospaceFonts,
];

export const fontsByCategory: Record<FontCategory, FontDefinition[]> = {
  'sans-serif': sansSerifFonts,
  serif: serifFonts,
  display: displayFonts,
  monospace: monospaceFonts,
};

export function getFontById(id: string): FontDefinition | undefined {
  return fontList.find((f) => f.id === id);
}

export function getFontByName(name: string): FontDefinition | undefined {
  return fontList.find((f) => f.name === name);
}

export function getGoogleFontName(font: FontDefinition): string {
  return font.name.replace(/ /g, '+');
}
