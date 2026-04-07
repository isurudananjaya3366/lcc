import type { Config } from 'tailwindcss';

const config: Config = {
  // ── Content Paths ────────────────────────────────────────────
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './stories/**/*.{js,ts,jsx,tsx}',
  ],

  // ── Dark Mode ────────────────────────────────────────────────
  darkMode: 'class',

  // ── Theme ────────────────────────────────────────────────────
  theme: {
    // ── Custom Breakpoints ───────────────────────────────────
    screens: {
      xs: '475px',
      // Defaults: sm(640), md(768), lg(1024), xl(1280), 2xl(1536)
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
      '3xl': '1920px',
    },

    extend: {
      // ── Font Families ────────────────────────────────────────
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'Consolas', 'monospace'],
        display: ['var(--font-display)', 'system-ui', 'sans-serif'],
      },

      // ── Extended Spacing ─────────────────────────────────────
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
        '30': '7.5rem',
      },

      // ── Brand Colors ─────────────────────────────────────────
      colors: {
        primary: {
          50: '#e6f0ff',
          100: '#b3d1ff',
          200: '#80b3ff',
          300: '#4d94ff',
          400: '#1a75ff',
          500: '#0066CC',
          600: '#0052a3',
          700: '#003d7a',
          800: '#002952',
          900: '#001429',
          950: '#000a14',
        },
        secondary: {
          50: '#e6f9f0',
          100: '#b3edcf',
          200: '#80e0af',
          300: '#4dd48e',
          400: '#1ac76d',
          500: '#00A86B',
          600: '#008756',
          700: '#006540',
          800: '#00432b',
          900: '#002215',
          950: '#00110b',
        },
        accent: {
          50: '#fff9e6',
          100: '#ffedb3',
          200: '#ffe180',
          300: '#ffd54d',
          400: '#ffc91a',
          500: '#FFB800',
          600: '#cc9300',
          700: '#996e00',
          800: '#664a00',
          900: '#332500',
          950: '#1a1300',
        },

        // ── Semantic Colors ────────────────────────────────────
        success: {
          50: '#ecfdf5',
          100: '#d1fae5',
          200: '#a7f3d0',
          300: '#6ee7b7',
          400: '#34d399',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          800: '#065f46',
          900: '#064e3b',
          950: '#022c22',
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        error: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        info: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554',
        },
      },
    },
  },

  // ── Plugins ──────────────────────────────────────────────────
  plugins: [],
};

export default config;
