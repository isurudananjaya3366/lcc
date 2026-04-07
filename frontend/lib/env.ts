/**
 * LankaCommerce Cloud — Frontend Environment Validation
 *
 * Runtime validation of environment variables using Zod v4.
 * This module ensures that all required environment variables are present
 * and correctly typed before the application starts.
 *
 * Usage:
 *   import { env } from "@/lib/env";
 *   const apiUrl = env.NEXT_PUBLIC_API_URL; // string, validated
 *
 * @see .env.local.example for variable documentation.
 * @see types/env.d.ts for TypeScript declarations.
 */

import { z } from 'zod';

// ════════════════════════════════════════════════════════════════════════
// HELPER SCHEMAS
// ════════════════════════════════════════════════════════════════════════

/** Coerce string boolean from env ("true"/"false") to actual boolean. */
const booleanString = z.stringbool().optional().default(false);

/** Optional string that defaults to empty string. */
const optionalString = z.string().optional().default('');

// ════════════════════════════════════════════════════════════════════════
// SERVER-SIDE ENVIRONMENT SCHEMA
// ════════════════════════════════════════════════════════════════════════
// Variables without NEXT_PUBLIC_ prefix — only available in server code
// (API routes, middleware, getServerSideProps, Server Components).

const serverSchema = z.object({
  NODE_ENV: z
    .enum(['development', 'production', 'test'])
    .default('development'),

  // ── API (server → backend) ──────────────────────────────────────────
  API_BASE_URL: z
    .string()
    .url()
    .optional()
    .default('http://backend:8000/api/v1'),
  API_TIMEOUT: z.coerce.number().int().positive().optional().default(30000),

  // ── Authentication ──────────────────────────────────────────────────
  NEXTAUTH_URL: z.string().url().optional().default('http://localhost:3000'),
  NEXTAUTH_SECRET: optionalString,

  // ── Payment Secrets (server-only) ───────────────────────────────────
  STRIPE_SECRET_KEY: optionalString,
  STRIPE_WEBHOOK_SECRET: optionalString,

  // ── Monitoring Secrets (server-only) ────────────────────────────────
  SENTRY_AUTH_TOKEN: optionalString,
});

// ════════════════════════════════════════════════════════════════════════
// CLIENT-SIDE ENVIRONMENT SCHEMA
// ════════════════════════════════════════════════════════════════════════
// Variables with NEXT_PUBLIC_ prefix — embedded in the JS bundle at build
// time and available in both server and client code.
//
// ⚠️ NEVER put secrets here — they are visible to anyone.

const clientSchema = z.object({
  // ── API (browser → backend) ─────────────────────────────────────────
  NEXT_PUBLIC_API_URL: z.string().url().default('http://localhost:8000/api/v1'),

  // ── WebSocket (real-time features) ──────────────────────────────────
  NEXT_PUBLIC_WS_URL: z.string().default('ws://localhost:8000/ws'),

  // ── Site ────────────────────────────────────────────────────────────
  NEXT_PUBLIC_SITE_URL: z.string().url().default('http://localhost:3000'),
  NEXT_PUBLIC_SITE_NAME: z.string().default('LankaCommerce Cloud'),
  NEXT_PUBLIC_APP_NAME: z.string().default('LCC'),
  NEXT_PUBLIC_SITE_DESCRIPTION: z
    .string()
    .default('Multi-tenant SaaS ERP for Sri Lankan SMEs'),

  // ── Authentication ──────────────────────────────────────────────────
  NEXT_PUBLIC_AUTH_COOKIE_NAME: z.string().default('lcc_auth'),
  NEXT_PUBLIC_TOKEN_EXPIRY_BUFFER: z.coerce
    .number()
    .int()
    .nonnegative()
    .default(60),

  // ── Feature Flags ───────────────────────────────────────────────────
  NEXT_PUBLIC_ENABLE_ANALYTICS: booleanString,
  NEXT_PUBLIC_ENABLE_AI_FEATURES: booleanString,
  NEXT_PUBLIC_ENABLE_WEBSTORE: z.stringbool().optional().default(true),
  NEXT_PUBLIC_ENABLE_POS: z.stringbool().optional().default(true),
  NEXT_PUBLIC_ENABLE_OFFLINE: z.stringbool().optional().default(true),
  NEXT_PUBLIC_DEBUG: booleanString,

  // ── Third-Party Services ────────────────────────────────────────────
  NEXT_PUBLIC_GA_TRACKING_ID: optionalString,
  NEXT_PUBLIC_SENTRY_DSN: optionalString,
  NEXT_PUBLIC_PAYHERE_MERCHANT_ID: optionalString,
  NEXT_PUBLIC_STRIPE_PUBLIC_KEY: optionalString,
  NEXT_PUBLIC_MAPS_API_KEY: optionalString,

  // ── Sri Lanka Localization ──────────────────────────────────────────
  NEXT_PUBLIC_DEFAULT_LOCALE: z.string().default('en-LK'),
  NEXT_PUBLIC_DEFAULT_TIMEZONE: z.string().default('Asia/Colombo'),
  NEXT_PUBLIC_DEFAULT_CURRENCY: z.string().default('LKR'),
  NEXT_PUBLIC_CURRENCY_SYMBOL: z.string().default('Rs.'),

  // ── Tenant ──────────────────────────────────────────────────────────
  NEXT_PUBLIC_DEFAULT_TENANT: z.string().default('demo'),
  NEXT_PUBLIC_TENANT_PATTERN: z.string().default('{tenant}.lankacommerce.lk'),

  // ── Image / CDN ─────────────────────────────────────────────────────
  NEXT_PUBLIC_IMAGE_DOMAIN: z.string().default('cdn.lankacommerce.lk'),
  NEXT_PUBLIC_CLOUDINARY_CLOUD: optionalString,
});

// ════════════════════════════════════════════════════════════════════════
// COMBINED SCHEMA
// ════════════════════════════════════════════════════════════════════════

const envSchema = serverSchema.merge(clientSchema);

// ════════════════════════════════════════════════════════════════════════
// VALIDATION
// ════════════════════════════════════════════════════════════════════════

/**
 * Validate and parse environment variables.
 * Throws a descriptive error at startup if required variables are missing.
 */
function validateEnv() {
  const result = envSchema.safeParse(process.env);

  if (!result.success) {
    const formatted = result.error.issues
      .map((issue) => `  ✗ ${issue.path.join('.')}: ${issue.message}`)
      .join('\n');

    console.error(
      '\n🚨 Invalid environment variables:\n' +
        formatted +
        '\n\n' +
        '💡 Check your .env.local file against .env.local.example.\n' +
        '   See frontend/README.md → Environment Variables for help.\n'
    );

    throw new Error('Invalid environment variables. See console output above.');
  }

  return result.data;
}

// ════════════════════════════════════════════════════════════════════════
// EXPORTS
// ════════════════════════════════════════════════════════════════════════

/**
 * Validated environment variables.
 * Import this instead of using `process.env` directly for type safety.
 *
 * @example
 * ```ts
 * import { env } from "@/lib/env";
 * fetch(env.NEXT_PUBLIC_API_URL + "/products");
 * ```
 */
export const env = validateEnv();

/** Re-export schemas for testing or external validation. */
export { clientSchema, envSchema, serverSchema };
