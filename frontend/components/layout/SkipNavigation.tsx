'use client';

/**
 * SkipNavigation — Accessibility skip link for keyboard/screen reader users.
 *
 * Allows users to bypass the sidebar and header and jump directly
 * to the main content area. WCAG 2.1 Level A requirement.
 *
 * - Visually hidden by default
 * - Becomes visible on :focus (Tab key)
 * - Links to #main-content anchor
 */
export function SkipNavigation() {
  return (
    <a
      href="#main-content"
      className="fixed left-2 top-[-40px] z-[9999] rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-lg transition-all duration-200 focus:top-2 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
    >
      Skip to main content
    </a>
  );
}
