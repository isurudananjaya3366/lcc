import type { Config } from 'tailwindcss';
import { fontFamily } from 'tailwindcss/defaultTheme';
import typography from '@tailwindcss/typography';
import forms from '@tailwindcss/forms';
import aspectRatio from '@tailwindcss/aspect-ratio';

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

    // ── Container ─────────────────────────────────────────
    container: {
      center: true,
      padding: {
        DEFAULT: '1rem',
        sm: '1rem',
        md: '1.5rem',
        lg: '2rem',
        xl: '2rem',
        '2xl': '2rem',
      },
    },

    extend: {
      // ── Font Families ────────────────────────────────────────
      fontFamily: {
        sans: [
          'var(--font-inter)',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Noto Sans"',
          '"Helvetica Neue"',
          'Arial',
          ...fontFamily.sans,
        ],
        mono: [
          'var(--font-mono)',
          '"SF Mono"',
          'Consolas',
          'Monaco',
          '"Liberation Mono"',
          '"Ubuntu Mono"',
          '"Courier New"',
          ...fontFamily.mono,
        ],
        display: ['var(--font-display)', ...fontFamily.sans],
      },

      // ── Font Size Scale (with line-height pairings) ──────────
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
        '5xl': ['3rem', { lineHeight: '1' }],
        '6xl': ['3.75rem', { lineHeight: '1' }],
        '7xl': ['4.5rem', { lineHeight: '1' }],
        '8xl': ['6rem', { lineHeight: '1' }],
        '9xl': ['8rem', { lineHeight: '1' }],
      },

      // ── Font Weight Scale ────────────────────────────────────
      fontWeight: {
        light: '300',
        normal: '400',
        medium: '500',
        semibold: '600',
        bold: '700',
      },

      // ── Letter Spacing Scale ─────────────────────────────────
      letterSpacing: {
        tighter: '-0.05em',
        tight: '-0.025em',
        normal: '0em',
        wide: '0.025em',
        wider: '0.05em',
        widest: '0.1em',
      },

      // ── Line Height Scale ────────────────────────────────────
      lineHeight: {
        none: '1',
        tight: '1.25',
        snug: '1.375',
        normal: '1.5',
        relaxed: '1.625',
        loose: '2',
      },

      // ── Typography Plugin (Prose) ────────────────────────────
      typography: {
        DEFAULT: {
          css: {
            '--tw-prose-body': 'hsl(var(--secondary-700))',
            '--tw-prose-headings': 'hsl(var(--secondary-900))',
            '--tw-prose-lead': 'hsl(var(--secondary-600))',
            '--tw-prose-links': 'hsl(var(--primary-600))',
            '--tw-prose-bold': 'hsl(var(--secondary-900))',
            '--tw-prose-counters': 'hsl(var(--secondary-500))',
            '--tw-prose-bullets': 'hsl(var(--secondary-500))',
            '--tw-prose-hr': 'hsl(var(--secondary-300))',
            '--tw-prose-quotes': 'hsl(var(--secondary-600))',
            '--tw-prose-quote-borders': 'hsl(var(--secondary-300))',
            '--tw-prose-captions': 'hsl(var(--secondary-500))',
            '--tw-prose-code': 'hsl(var(--primary-600))',
            '--tw-prose-pre-code': 'hsl(var(--secondary-100))',
            '--tw-prose-pre-bg': 'hsl(var(--secondary-900))',
            '--tw-prose-th-borders': 'hsl(var(--secondary-300))',
            '--tw-prose-td-borders': 'hsl(var(--secondary-200))',
            '--tw-prose-invert-body': 'hsl(var(--secondary-300))',
            '--tw-prose-invert-headings': 'hsl(var(--secondary-100))',
            '--tw-prose-invert-lead': 'hsl(var(--secondary-400))',
            '--tw-prose-invert-links': 'hsl(var(--primary-400))',
            '--tw-prose-invert-bold': 'hsl(var(--secondary-100))',
            '--tw-prose-invert-counters': 'hsl(var(--secondary-400))',
            '--tw-prose-invert-bullets': 'hsl(var(--secondary-500))',
            '--tw-prose-invert-hr': 'hsl(var(--secondary-700))',
            '--tw-prose-invert-quotes': 'hsl(var(--secondary-400))',
            '--tw-prose-invert-quote-borders': 'hsl(var(--secondary-700))',
            '--tw-prose-invert-captions': 'hsl(var(--secondary-500))',
            '--tw-prose-invert-code': 'hsl(var(--primary-400))',
            '--tw-prose-invert-pre-code': 'hsl(var(--secondary-100))',
            '--tw-prose-invert-pre-bg': 'hsl(var(--secondary-950))',
            '--tw-prose-invert-th-borders': 'hsl(var(--secondary-700))',
            '--tw-prose-invert-td-borders': 'hsl(var(--secondary-800))',
            a: {
              '&:hover': {
                color: 'hsl(var(--primary-700))',
              },
            },
            code: {
              backgroundColor: 'hsl(var(--secondary-100))',
              borderRadius: '0.25rem',
              padding: '0.125rem 0.375rem',
              fontWeight: '500',
            },
            'code::before': { content: '""' },
            'code::after': { content: '""' },
            blockquote: {
              fontStyle: 'italic',
            },
            'thead th': {
              backgroundColor: 'hsl(var(--secondary-100))',
            },
          },
        },
      },

      // ── Extended Spacing (4px base unit) ──────────────────────
      spacing: {
        '0.5': '0.125rem',
        '1.5': '0.375rem',
        '2.5': '0.625rem',
        '3.5': '0.875rem',
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
        '30': '7.5rem',
      },

      // ── Max Width Scale ──────────────────────────────────────
      maxWidth: {
        prose: '65ch',
      },

      // ── Container Settings ───────────────────────────────────

      // ── Border Radius Scale ──────────────────────────────────
      borderRadius: {
        none: '0',
        sm: '0.125rem',
        DEFAULT: '0.375rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
        full: '9999px',
      },

      // ── Box Shadow Scale ─────────────────────────────────────
      boxShadow: {
        sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
        DEFAULT:
          '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        '2xl': '0 25px 50px -12px rgb(0 0 0 / 0.25)',
        inner: 'inset 0 2px 4px 0 rgb(0 0 0 / 0.06)',
        none: '0 0 #0000',
      },

      // ── Z-Index Scale ────────────────────────────────────────
      zIndex: {
        dropdown: '50',
        sticky: '100',
        fixed: '150',
        'modal-backdrop': '200',
        modal: '250',
        popover: '300',
        tooltip: '350',
        toast: '400',
      },

      // ── Transition Duration Scale ────────────────────────────
      transitionDuration: {
        '75': '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '300': '300ms',
        '500': '500ms',
      },

      // ── Transition Timing Functions ──────────────────────────
      transitionTimingFunction: {
        'ease-in': 'cubic-bezier(0.4, 0, 1, 1)',
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)',
        'ease-in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
        sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
        smooth: 'cubic-bezier(0.4, 0, 0.1, 1)',
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },

      // ── Animation Keyframes ──────────────────────────────────
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'fade-out': {
          from: { opacity: '1' },
          to: { opacity: '0' },
        },
        'slide-in-up': {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-down': {
          from: { opacity: '0', transform: 'translateY(-10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-left': {
          from: { opacity: '0', transform: 'translateX(-10px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        'slide-in-right': {
          from: { opacity: '0', transform: 'translateX(10px)' },
          to: { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        spin: {
          from: { transform: 'rotate(0deg)' },
          to: { transform: 'rotate(360deg)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        shake: {
          '0%, 100%': { transform: 'translateX(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateX(-4px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateX(4px)' },
        },
        'shake-y': {
          '0%, 100%': { transform: 'translateY(0)' },
          '10%, 30%, 50%, 70%, 90%': { transform: 'translateY(-4px)' },
          '20%, 40%, 60%, 80%': { transform: 'translateY(4px)' },
        },
        'scale-in-center': {
          '0%': { opacity: '0', transform: 'scale(0.8)' },
          '80%': { opacity: '1', transform: 'scale(1.02)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        'pulse-glow': {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
      },

      // ── Animation Utilities ──────────────────────────────────
      animation: {
        'fade-in': 'fade-in 200ms ease-out',
        'fade-in-fast': 'fade-in 100ms ease-out',
        'fade-in-slow': 'fade-in 300ms ease-out',
        'fade-out': 'fade-out 200ms ease-in',
        'slide-in-up': 'slide-in-up 300ms ease-out',
        'slide-in-up-fast': 'slide-in-up 150ms ease-out',
        'slide-in-down': 'slide-in-down 300ms ease-out',
        'slide-in-left': 'slide-in-left 300ms ease-out',
        'slide-in-right': 'slide-in-right 300ms ease-out',
        'scale-in': 'scale-in 200ms ease-out',
        'scale-in-center': 'scale-in-center 300ms ease-out',
        'scale-in-fast': 'scale-in 100ms ease-out',
        'scale-in-slow': 'scale-in 400ms ease-out',
        spin: 'spin 1s linear infinite',
        'spin-fast': 'spin 500ms linear infinite',
        'spin-slow': 'spin 2s linear infinite',
        pulse: 'pulse 2s ease-in-out infinite',
        'pulse-fast': 'pulse 1s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        shake: 'shake 500ms ease-in-out',
        'shake-slow': 'shake 800ms ease-in-out',
        'shake-y': 'shake-y 500ms ease-in-out',
      },

      // ── Brand Colors (CSS Variable Integration) ──────────────
      colors: {
        // Semantic surface colors
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },

        // Brand palettes
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
          50: 'hsl(var(--primary-50))',
          100: 'hsl(var(--primary-100))',
          200: 'hsl(var(--primary-200))',
          300: 'hsl(var(--primary-300))',
          400: 'hsl(var(--primary-400))',
          500: 'hsl(var(--primary-500))',
          600: 'hsl(var(--primary-600))',
          700: 'hsl(var(--primary-700))',
          800: 'hsl(var(--primary-800))',
          900: 'hsl(var(--primary-900))',
          950: 'hsl(var(--primary-950))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
          50: 'hsl(var(--secondary-50))',
          100: 'hsl(var(--secondary-100))',
          200: 'hsl(var(--secondary-200))',
          300: 'hsl(var(--secondary-300))',
          400: 'hsl(var(--secondary-400))',
          500: 'hsl(var(--secondary-500))',
          600: 'hsl(var(--secondary-600))',
          700: 'hsl(var(--secondary-700))',
          800: 'hsl(var(--secondary-800))',
          900: 'hsl(var(--secondary-900))',
          950: 'hsl(var(--secondary-950))',
        },

        // State colors
        success: {
          DEFAULT: 'hsl(var(--success))',
          foreground: 'hsl(var(--success-foreground))',
          50: 'hsl(var(--success-50))',
          100: 'hsl(var(--success-100))',
          200: 'hsl(var(--success-200))',
          300: 'hsl(var(--success-300))',
          400: 'hsl(var(--success-400))',
          500: 'hsl(var(--success-500))',
          600: 'hsl(var(--success-600))',
          700: 'hsl(var(--success-700))',
          800: 'hsl(var(--success-800))',
          900: 'hsl(var(--success-900))',
          950: 'hsl(var(--success-950))',
        },
        warning: {
          DEFAULT: 'hsl(var(--warning))',
          foreground: 'hsl(var(--warning-foreground))',
          50: 'hsl(var(--warning-50))',
          100: 'hsl(var(--warning-100))',
          200: 'hsl(var(--warning-200))',
          300: 'hsl(var(--warning-300))',
          400: 'hsl(var(--warning-400))',
          500: 'hsl(var(--warning-500))',
          600: 'hsl(var(--warning-600))',
          700: 'hsl(var(--warning-700))',
          800: 'hsl(var(--warning-800))',
          900: 'hsl(var(--warning-900))',
          950: 'hsl(var(--warning-950))',
        },
        error: {
          DEFAULT: 'hsl(var(--error))',
          foreground: 'hsl(var(--error-foreground))',
          50: 'hsl(var(--error-50))',
          100: 'hsl(var(--error-100))',
          200: 'hsl(var(--error-200))',
          300: 'hsl(var(--error-300))',
          400: 'hsl(var(--error-400))',
          500: 'hsl(var(--error-500))',
          600: 'hsl(var(--error-600))',
          700: 'hsl(var(--error-700))',
          800: 'hsl(var(--error-800))',
          900: 'hsl(var(--error-900))',
          950: 'hsl(var(--error-950))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        info: {
          DEFAULT: 'hsl(var(--info))',
          foreground: 'hsl(var(--info-foreground))',
          50: 'hsl(var(--info-50))',
          100: 'hsl(var(--info-100))',
          200: 'hsl(var(--info-200))',
          300: 'hsl(var(--info-300))',
          400: 'hsl(var(--info-400))',
          500: 'hsl(var(--info-500))',
          600: 'hsl(var(--info-600))',
          700: 'hsl(var(--info-700))',
          800: 'hsl(var(--info-800))',
          900: 'hsl(var(--info-900))',
          950: 'hsl(var(--info-950))',
        },

        // Border colors
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',

        // Chart colors
        chart: {
          1: 'hsl(var(--chart-1))',
          2: 'hsl(var(--chart-2))',
          3: 'hsl(var(--chart-3))',
          4: 'hsl(var(--chart-4))',
          5: 'hsl(var(--chart-5))',
        },

        // Status colors
        status: {
          pending: 'hsl(var(--status-pending))',
          processing: 'hsl(var(--status-processing))',
          completed: 'hsl(var(--status-completed))',
          cancelled: 'hsl(var(--status-cancelled))',
          failed: 'hsl(var(--status-failed))',
          draft: 'hsl(var(--status-draft))',
          archived: 'hsl(var(--status-archived))',
          new: 'hsl(var(--status-new))',
        },
      },
    },
  },

  // ── Plugins ──────────────────────────────────────────────────
  plugins: [typography, forms, aspectRatio],
};

export default config;
