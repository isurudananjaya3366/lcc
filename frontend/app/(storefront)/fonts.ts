import { Inter, JetBrains_Mono } from 'next/font/google';

/**
 * Primary body font — used for all body text and UI elements.
 * Also used for headings (same family, different weights).
 */
export const fontBody = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  display: 'swap',
  variable: '--font-body',
});

/**
 * Monospace font — used for prices, SKUs, codes, and technical content.
 */
export const fontMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500'],
  display: 'swap',
  variable: '--font-mono',
});

/**
 * Combined font class names for applying to root element.
 * Usage: `<body className={storeFontClassNames}>...</body>`
 */
export const storeFontClassNames = `${fontBody.variable} ${fontMono.variable}`;
