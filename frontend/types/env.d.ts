/**
 * Environment variable type declarations for LankaCommerce Cloud.
 *
 * Extends NodeJS.ProcessEnv with application-specific environment
 * variables for type-safe access via process.env.
 *
 * NEXT_PUBLIC_ variables are available in both server and client code.
 * Variables without the prefix are server-side only.
 *
 * @see .env.local.example for variable descriptions and defaults.
 */

declare namespace NodeJS {
  interface ProcessEnv {
    // ── Next.js Built-in ─────────────────────────────────────
    readonly NODE_ENV: "development" | "production" | "test";

    // ── API Configuration ────────────────────────────────────
    /** Backend API base URL (client-side, from browser). */
    readonly NEXT_PUBLIC_API_URL: string;
    /** WebSocket URL for real-time features (notifications, live updates, POS sync). */
    readonly NEXT_PUBLIC_WS_URL?: string;
    /** Backend API base URL (server-side, Docker network). */
    readonly API_BASE_URL?: string;
    /** API request timeout in milliseconds. */
    readonly API_TIMEOUT?: string;

    // ── Site Configuration ───────────────────────────────────
    /** Canonical frontend URL. */
    readonly NEXT_PUBLIC_SITE_URL: string;
    /** Application display name (full). */
    readonly NEXT_PUBLIC_SITE_NAME?: string;
    /** Short application name for PWA, browser tabs, mobile home screen. */
    readonly NEXT_PUBLIC_APP_NAME?: string;
    /** Application description for SEO. */
    readonly NEXT_PUBLIC_SITE_DESCRIPTION?: string;

    // ── Authentication ───────────────────────────────────────
    /** Auth cookie name. */
    readonly NEXT_PUBLIC_AUTH_COOKIE_NAME?: string;
    /** Seconds before token expiry to trigger refresh. */
    readonly NEXT_PUBLIC_TOKEN_EXPIRY_BUFFER?: string;
    /** NextAuth.js callback URL. */
    readonly NEXTAUTH_URL?: string;
    /** NextAuth.js signing secret (server-side only, REQUIRED in prod). */
    readonly NEXTAUTH_SECRET?: string;

    // ── Feature Flags ────────────────────────────────────────
    /** Enable analytics tracking. */
    readonly NEXT_PUBLIC_ENABLE_ANALYTICS?: string;
    /** Enable AI-powered features. */
    readonly NEXT_PUBLIC_ENABLE_AI_FEATURES?: string;
    /** Enable webstore module. */
    readonly NEXT_PUBLIC_ENABLE_WEBSTORE?: string;
    /** Enable POS module. */
    readonly NEXT_PUBLIC_ENABLE_POS?: string;
    /** Enable offline mode / PWA support. */
    readonly NEXT_PUBLIC_ENABLE_OFFLINE?: string;
    /** Enable debug mode (verbose logging). */
    readonly NEXT_PUBLIC_DEBUG?: string;

    // ── Third-Party Services ─────────────────────────────────
    /** Google Analytics 4 tracking ID (G-XXXXXXXXXX). */
    readonly NEXT_PUBLIC_GA_TRACKING_ID?: string;
    /** Sentry DSN for error tracking. */
    readonly NEXT_PUBLIC_SENTRY_DSN?: string;
    /** PayHere merchant ID (Sri Lanka payments). */
    readonly NEXT_PUBLIC_PAYHERE_MERCHANT_ID?: string;
    /** Stripe publishable key (pk_test_... or pk_live_...). */
    readonly NEXT_PUBLIC_STRIPE_PUBLIC_KEY?: string;
    /** Google Maps JavaScript API key for store locator, delivery tracking. */
    readonly NEXT_PUBLIC_MAPS_API_KEY?: string;

    // ── Sri Lanka Localization ───────────────────────────────
    /** Default BCP 47 locale (e.g., en-LK). */
    readonly NEXT_PUBLIC_DEFAULT_LOCALE?: string;
    /** Default IANA timezone (Asia/Colombo). */
    readonly NEXT_PUBLIC_DEFAULT_TIMEZONE?: string;
    /** Default ISO 4217 currency code (LKR). */
    readonly NEXT_PUBLIC_DEFAULT_CURRENCY?: string;
    /** Currency display symbol (Rs.). */
    readonly NEXT_PUBLIC_CURRENCY_SYMBOL?: string;

    // ── Tenant Configuration ─────────────────────────────────
    /** Default tenant slug. */
    readonly NEXT_PUBLIC_DEFAULT_TENANT?: string;
    /** Tenant URL pattern (e.g., {tenant}.lankacommerce.lk). */
    readonly NEXT_PUBLIC_TENANT_PATTERN?: string;

    // ── Image / CDN ──────────────────────────────────────────
    /** Allowed image domain for next/image. */
    readonly NEXT_PUBLIC_IMAGE_DOMAIN?: string;
    /** Cloudinary cloud name (if using Cloudinary). */
    readonly NEXT_PUBLIC_CLOUDINARY_CLOUD?: string;

    // ── Server-Only Secrets ──────────────────────────────────
    /** Stripe secret key for server-side payment processing (sk_test_... or sk_live_...). */
    readonly STRIPE_SECRET_KEY?: string;
    /** Stripe webhook signing secret for verifying event signatures (whsec_...). */
    readonly STRIPE_WEBHOOK_SECRET?: string;
    /** Sentry auth token for source map uploads during build (sntrys_...). */
    readonly SENTRY_AUTH_TOKEN?: string;
  }
}
