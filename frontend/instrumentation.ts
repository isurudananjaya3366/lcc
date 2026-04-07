/**
 * Next.js Instrumentation — runs once on server startup.
 *
 * This file triggers environment variable validation before any
 * requests are processed. If validation fails, the application
 * will throw an error and refuse to start.
 *
 * @see https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation
 * @see lib/env.ts for the validation schema.
 */

export async function register() {
  // Validate environment variables on server startup.
  // This import triggers the validation in lib/env.ts.
  // If any required variables are missing or invalid, the server
  // will fail fast with a descriptive error message.
  await import('@/lib/env');

  if (process.env.NODE_ENV === 'development') {
    console.log('✅ Environment variables validated successfully');
  }
}
