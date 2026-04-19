'use client';

// ================================================================
// Preview Frame (Task 82)
// ================================================================
// Iframe-based preview that renders the storefront with the
// current theme's CSS variables injected.
// ================================================================

import React, { useRef, useCallback, useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/storefront/useTheme';
import type { Theme } from '@/types/storefront/theme.types';

// ─── Types ──────────────────────────────────────────────────────

export interface PreviewFrameProps {
  viewport: 'desktop' | 'mobile';
  className?: string;
  onLoad?: () => void;
}

// ─── CSS Generation ─────────────────────────────────────────────

function generateThemeCss(theme: Theme): string {
  const { colors, fonts } = theme;

  return `
:root {
  /* Primary Colors */
  --color-primary: ${colors.primary};
  --color-secondary: ${colors.secondary};
  --color-accent: ${colors.accent};
  --color-background: ${colors.background};
  --color-surface: ${colors.surface};

  /* Text Colors */
  --color-text-primary: ${colors.text.primary};
  --color-text-secondary: ${colors.text.secondary};
  --color-text-disabled: ${colors.text.disabled};

  /* Border Colors */
  --color-border-light: ${colors.border.light};
  --color-border-dark: ${colors.border.dark};

  /* Status Colors */
  --color-success: ${colors.status.success};
  --color-warning: ${colors.status.warning};
  --color-error: ${colors.status.error};
  --color-info: ${colors.status.info};

  /* Typography */
  --font-heading: '${fonts.heading}', sans-serif;
  --font-body: '${fonts.body}', sans-serif;
  --font-scale: ${fonts.scale};
  --font-weight-light: ${fonts.weights.light};
  --font-weight-normal: ${fonts.weights.normal};
  --font-weight-medium: ${fonts.weights.medium};
  --font-weight-bold: ${fonts.weights.bold};
}

body {
  font-family: var(--font-body);
  background-color: var(--color-background);
  color: var(--color-text-primary);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
}
`.trim();
}

function buildPreviewHtml(theme: Theme): string {
  const css = generateThemeCss(theme);
  const { colors, fonts, logo, homepage } = theme;

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>${css}</style>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { min-height: 100vh; }
    .header {
      background: var(--color-surface);
      border-bottom: 1px solid var(--color-border-light);
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .logo { font-family: var(--font-heading); font-size: 1.25rem; font-weight: var(--font-weight-bold); color: var(--color-primary); }
    .nav { display: flex; gap: 1.5rem; }
    .nav a { color: var(--color-text-secondary); text-decoration: none; font-size: 0.875rem; }
    .hero {
      background: var(--color-primary);
      color: #fff;
      padding: 4rem 2rem;
      text-align: center;
    }
    .hero h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    .hero p { opacity: 0.9; margin-bottom: 1.5rem; }
    .hero .cta {
      display: inline-block;
      background: var(--color-accent);
      color: #fff;
      padding: 0.75rem 2rem;
      border-radius: 0.375rem;
      text-decoration: none;
      font-weight: var(--font-weight-medium);
    }
    .products { padding: 2rem; }
    .products h2 { margin-bottom: 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
    .card {
      background: var(--color-surface);
      border: 1px solid var(--color-border-light);
      border-radius: 0.5rem;
      padding: 1rem;
    }
    .card .swatch { height: 120px; background: var(--color-secondary); border-radius: 0.375rem; margin-bottom: 0.75rem; }
    .card .title { font-weight: var(--font-weight-medium); margin-bottom: 0.25rem; }
    .card .price { color: var(--color-primary); font-weight: var(--font-weight-bold); }
    .footer {
      background: var(--color-surface);
      border-top: 1px solid var(--color-border-light);
      padding: 2rem;
      text-align: center;
      color: var(--color-text-secondary);
      font-size: 0.75rem;
    }
  </style>
</head>
<body>
  <header class="header">
    <span class="logo">${logo?.alt || theme.name || 'Store'}</span>
    <nav class="nav">
      <a href="#">Home</a>
      <a href="#">Products</a>
      <a href="#">About</a>
      <a href="#">Contact</a>
    </nav>
  </header>

  <section class="hero">
    <h1>${homepage?.hero?.title || 'Welcome to Our Store'}</h1>
    <p>${homepage?.hero?.subtitle || 'Discover amazing products at great prices'}</p>
    <a class="cta" href="#">${homepage?.hero?.ctaText || 'Shop Now'}</a>
  </section>

  <section class="products">
    <h2>${homepage?.featuredProducts?.title || 'Featured Products'}</h2>
    <div class="grid">
      <div class="card"><div class="swatch"></div><div class="title">Product 1</div><div class="price">$29.99</div></div>
      <div class="card"><div class="swatch"></div><div class="title">Product 2</div><div class="price">$49.99</div></div>
      <div class="card"><div class="swatch"></div><div class="title">Product 3</div><div class="price">$19.99</div></div>
      <div class="card"><div class="swatch"></div><div class="title">Product 4</div><div class="price">$39.99</div></div>
    </div>
  </section>

  <footer class="footer">
    &copy; 2026 ${theme.name || 'Store'}. All rights reserved.
  </footer>
</body>
</html>`;
}

// ─── Component ──────────────────────────────────────────────────

export function PreviewFrame({ viewport, className, onLoad }: PreviewFrameProps) {
  const { theme } = useTheme();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleLoad = useCallback(() => {
    setIsLoading(false);
    onLoad?.();
  }, [onLoad]);

  // Re-inject CSS when theme changes without full reload
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe || !theme) return;

    try {
      const doc = iframe.contentDocument;
      if (!doc) return;

      let styleEl = doc.getElementById('theme-preview-styles');
      if (styleEl) {
        styleEl.textContent = generateThemeCss(theme);
      }
    } catch {
      // Cross-origin restriction – fall back to srcdoc update
    }
  }, [theme]);

  if (!theme) {
    return (
      <div
        className={cn('flex items-center justify-center rounded-lg border bg-muted p-8', className)}
      >
        <p className="text-sm text-muted-foreground">No theme loaded</p>
      </div>
    );
  }

  const srcdoc = buildPreviewHtml(theme);

  const iframeWidth = viewport === 'mobile' ? '375px' : '100%';
  const iframeHeight = viewport === 'mobile' ? '667px' : '100%';

  return (
    <div
      className={cn(
        'relative flex items-start justify-center',
        viewport === 'desktop' ? 'h-full w-full' : 'h-full w-full',
        className
      )}
    >
      {isLoading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/60">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        </div>
      )}

      <iframe
        ref={iframeRef}
        srcDoc={srcdoc}
        title="Theme Preview"
        sandbox="allow-scripts"
        onLoad={handleLoad}
        style={{
          width: iframeWidth,
          height: iframeHeight,
          minHeight: viewport === 'mobile' ? '667px' : '500px',
        }}
        className={cn('rounded-lg border bg-white', viewport === 'mobile' && 'mx-auto shadow-lg')}
      />
    </div>
  );
}
