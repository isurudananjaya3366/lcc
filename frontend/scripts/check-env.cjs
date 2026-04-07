#!/usr/bin/env node

/**
 * Frontend Environment Variable Validation Script
 *
 * Validates required, important, and optional environment variables
 * for the Next.js frontend application.
 *
 * Usage:
 *   node scripts/check-env.js              # Standard validation
 *   node scripts/check-env.js --strict     # Production-level validation
 *   node scripts/check-env.js --env-file .env.production
 *
 * Exit codes:
 *   0 — All validations passed
 *   1 — One or more validations failed
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ─── ANSI Color Helpers ───────────────────────────────────────────────────────

const isTTY = process.stdout.isTTY;

const colors = {
  reset: isTTY ? '\x1b[0m' : '',
  bold: isTTY ? '\x1b[1m' : '',
  dim: isTTY ? '\x1b[2m' : '',
  red: isTTY ? '\x1b[31m' : '',
  green: isTTY ? '\x1b[32m' : '',
  yellow: isTTY ? '\x1b[33m' : '',
  blue: isTTY ? '\x1b[34m' : '',
  cyan: isTTY ? '\x1b[36m' : '',
  white: isTTY ? '\x1b[37m' : '',
};

function colorize(color, text) {
  return `${colors[color]}${text}${colors.reset}`;
}

const icons = {
  pass: colorize('green', '✔'),
  fail: colorize('red', '✖'),
  warn: colorize('yellow', '⚠'),
  info: colorize('blue', 'ℹ'),
  arrow: colorize('dim', '→'),
};

// ─── CLI Argument Parsing ─────────────────────────────────────────────────────

const args = process.argv.slice(2);
const isStrict = args.includes('--strict');

let customEnvFile = null;
const envFileIndex = args.indexOf('--env-file');
if (envFileIndex !== -1 && args[envFileIndex + 1]) {
  customEnvFile = args[envFileIndex + 1];
}

if (args.includes('--help') || args.includes('-h')) {
  console.log(`
${colorize('bold', 'Frontend Environment Validation Script')}

${colorize('cyan', 'Usage:')}
  node scripts/check-env.js              Standard validation
  node scripts/check-env.js --strict     Production-level validation
  node scripts/check-env.js --env-file PATH   Use a custom .env file
  node scripts/check-env.js --help       Show this help message

${colorize('cyan', 'Description:')}
  Validates environment variables required by the Next.js frontend.
  Separates client-exposed (NEXT_PUBLIC_) from server-only variables.
  Warns about potential secrets leaked in NEXT_PUBLIC_ variables.
`);
  process.exit(0);
}

// ─── .env File Parser ─────────────────────────────────────────────────────────

/**
 * Parses a .env file into a key-value object.
 * Handles comments, empty lines, quoted values, and inline comments.
 */
function parseEnvFile(filePath) {
  const vars = {};
  if (!fs.existsSync(filePath)) {
    return vars;
  }

  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split(/\r?\n/);

  for (const rawLine of lines) {
    const line = rawLine.trim();

    // Skip empty lines and comments
    if (!line || line.startsWith('#')) {
      continue;
    }

    const eqIndex = line.indexOf('=');
    if (eqIndex === -1) {
      continue;
    }

    const key = line.slice(0, eqIndex).trim();
    let value = line.slice(eqIndex + 1).trim();

    // Handle quoted values
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    } else {
      // Strip inline comments for unquoted values
      const hashIndex = value.indexOf(' #');
      if (hashIndex !== -1) {
        value = value.slice(0, hashIndex).trim();
      }
    }

    vars[key] = value;
  }

  return vars;
}

// ─── Load Environment Variables ───────────────────────────────────────────────

const frontendDir = path.resolve(__dirname, '..');

// Determine which env file(s) to load
const envFilesToLoad = [];

if (customEnvFile) {
  const customPath = path.isAbsolute(customEnvFile)
    ? customEnvFile
    : path.resolve(process.cwd(), customEnvFile);
  envFilesToLoad.push(customPath);
} else {
  // Default: load .env then .env.local (local overrides base)
  const dotEnvPath = path.join(frontendDir, '.env');
  const dotEnvLocalPath = path.join(frontendDir, '.env.local');
  envFilesToLoad.push(dotEnvPath, dotEnvLocalPath);
}

// Merge file vars with process.env (process.env takes precedence)
let fileVars = {};

for (const envFile of envFilesToLoad) {
  if (fs.existsSync(envFile)) {
    const parsed = parseEnvFile(envFile);
    fileVars = { ...fileVars, ...parsed };
    console.log(`${icons.info} Loaded env file: ${colorize('dim', envFile)}`);
  } else if (customEnvFile) {
    console.log(
      `${icons.warn} Custom env file not found: ${colorize('yellow', envFile)}`
    );
  }
}

// Merged env: file vars as base, process.env overrides
const env = { ...fileVars, ...process.env };

// ─── Validation Helpers ───────────────────────────────────────────────────────

/**
 * Tests if a string is a valid URL (http or https).
 */
function isValidURL(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Tests if a string is a valid WebSocket URL (ws or wss).
 */
function isValidWSURL(value) {
  try {
    const url = new URL(value);
    return url.protocol === 'ws:' || url.protocol === 'wss:';
  } catch {
    return false;
  }
}

/**
 * Tests if a string matches BCP 47 locale format (e.g., en, en-US, en-LK).
 */
function isBCP47Locale(value) {
  return /^[a-z]{2,3}(-[A-Za-z]{2,4})?$/.test(value);
}

/**
 * Tests if a string looks like an IANA timezone (e.g., Asia/Colombo, UTC).
 */
function isIANATimezone(value) {
  return /^[A-Za-z_]+\/[A-Za-z_]+$/.test(value) || value === 'UTC';
}

/**
 * Tests if a string is a valid ISO 4217 currency code (3 uppercase letters).
 */
function isISO4217(value) {
  return /^[A-Z]{3}$/.test(value);
}

/**
 * Tests if a string is "true" or "false".
 */
function isBooleanString(value) {
  return value === 'true' || value === 'false';
}

/**
 * Tests if a string is a positive integer.
 */
function isPositiveInteger(value) {
  return /^\d+$/.test(value) && parseInt(value, 10) > 0;
}

/**
 * Tests if a string matches Google Analytics 4 tracking ID format.
 */
function isGA4TrackingID(value) {
  return /^G-[A-Z0-9]{8,12}$/.test(value);
}

/**
 * Tests if a string starts with sk_ (Stripe secret key format).
 */
function isStripeSecretKey(value) {
  return value.startsWith('sk_');
}

// ─── Security Check ───────────────────────────────────────────────────────────

const SECRET_PATTERNS = [
  { pattern: /secret/i, label: "contains 'secret'" },
  { pattern: /password/i, label: "contains 'password'" },
  { pattern: /^sk_/i, label: "starts with 'sk_' (looks like a secret key)" },
  { pattern: /private/i, label: "contains 'private'" },
];

/**
 * Checks if a NEXT_PUBLIC_ variable's value looks like it contains a secret.
 */
function checkForLeakedSecrets(key, value) {
  const warnings = [];
  for (const { pattern, label } of SECRET_PATTERNS) {
    if (pattern.test(value)) {
      warnings.push(
        `${icons.warn} ${colorize('yellow', 'SECURITY')} — ` +
          `${colorize('bold', key)} value ${label}. ` +
          `NEXT_PUBLIC_ variables are exposed to the browser!`
      );
    }
  }
  return warnings;
}

// ─── Validation Engine ────────────────────────────────────────────────────────

const results = {
  errors: [],
  warnings: [],
  passed: [],
  securityWarnings: [],
};

/**
 * Validates a single environment variable.
 *
 * @param {string}   key          Variable name
 * @param {object}   opts
 * @param {boolean}  opts.required       Whether the variable must be set
 * @param {function} opts.validate       Custom validation function (value) => boolean
 * @param {string}   opts.formatHint     Human-readable expected format
 * @param {boolean}  opts.requiredStrict Required only in --strict mode
 * @param {boolean}  opts.optional       Only validate format if present
 * @param {string}   opts.category       Display grouping label
 */
function check(key, opts = {}) {
  const {
    required = false,
    validate = null,
    formatHint = '',
    requiredStrict = false,
    optional = false,
    category = '',
  } = opts;

  const value = env[key];
  const isSet = value !== undefined && value !== '';

  // Run security check on NEXT_PUBLIC_ vars
  if (key.startsWith('NEXT_PUBLIC_') && isSet) {
    const secWarnings = checkForLeakedSecrets(key, value);
    results.securityWarnings.push(...secWarnings);
  }

  // Determine if the variable is required in the current mode
  const isRequired = required || (requiredStrict && isStrict);

  // Optional: skip if not set
  if (optional && !isSet) {
    results.passed.push({
      key,
      message: `${icons.pass} ${colorize('dim', key)} ${icons.arrow} not set ${colorize('dim', '(optional, skipped)')}`,
      category,
    });
    return;
  }

  // Check presence
  if (!isSet) {
    if (isRequired) {
      results.errors.push({
        key,
        message:
          `${icons.fail} ${colorize('red', key)} — ` +
          `is required${requiredStrict && isStrict ? ' in strict/production mode' : ''} but is not set` +
          (formatHint
            ? ` ${colorize('dim', `(expected: ${formatHint})`)}`
            : ''),
        category,
      });
    } else {
      results.warnings.push({
        key,
        message:
          `${icons.warn} ${colorize('yellow', key)} — ` +
          `not set (recommended)` +
          (formatHint
            ? ` ${colorize('dim', `(expected: ${formatHint})`)}`
            : ''),
        category,
      });
    }
    return;
  }

  // Check format
  if (validate && !validate(value)) {
    results.errors.push({
      key,
      message:
        `${icons.fail} ${colorize('red', key)} — ` +
        `invalid value "${colorize('yellow', value)}"` +
        (formatHint ? ` ${colorize('dim', `(expected: ${formatHint})`)}` : ''),
      category,
    });
    return;
  }

  // Passed
  results.passed.push({
    key,
    message: `${icons.pass} ${colorize('green', key)} ${icons.arrow} ${colorize('dim', truncate(value, 60))}`,
    category,
  });
}

function truncate(str, maxLen) {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 3) + '...';
}

// ─── Run Validations ──────────────────────────────────────────────────────────

console.log('');
console.log(
  colorize('bold', '══════════════════════════════════════════════════════════')
);
console.log(
  colorize('bold', '  Frontend Environment Validation') +
    (isStrict ? colorize('red', ' [STRICT MODE]') : '')
);
console.log(
  colorize('bold', '══════════════════════════════════════════════════════════')
);
console.log('');

// ── Required Client Variables (NEXT_PUBLIC_) ──────────────────────────────────

const CAT_CLIENT_REQUIRED = 'Required Client Variables (NEXT_PUBLIC_)';

check('NEXT_PUBLIC_API_URL', {
  required: true,
  validate: isValidURL,
  formatHint: 'valid HTTP(S) URL',
  category: CAT_CLIENT_REQUIRED,
});

check('NEXT_PUBLIC_SITE_URL', {
  required: true,
  validate: isValidURL,
  formatHint: 'valid HTTP(S) URL',
  category: CAT_CLIENT_REQUIRED,
});

// ── Important Client Variables ────────────────────────────────────────────────

const CAT_CLIENT_IMPORTANT = 'Important Client Variables (NEXT_PUBLIC_)';

check('NEXT_PUBLIC_SITE_NAME', {
  formatHint: 'non-empty string',
  category: CAT_CLIENT_IMPORTANT,
});

check('NEXT_PUBLIC_APP_NAME', {
  formatHint: 'non-empty string',
  category: CAT_CLIENT_IMPORTANT,
});

check('NEXT_PUBLIC_DEFAULT_LOCALE', {
  validate: isBCP47Locale,
  formatHint: 'BCP 47 locale, e.g. en-LK',
  category: CAT_CLIENT_IMPORTANT,
});

check('NEXT_PUBLIC_DEFAULT_TIMEZONE', {
  validate: isIANATimezone,
  formatHint: 'IANA timezone, e.g. Asia/Colombo',
  category: CAT_CLIENT_IMPORTANT,
});

check('NEXT_PUBLIC_DEFAULT_CURRENCY', {
  validate: isISO4217,
  formatHint: 'ISO 4217 currency code (3 uppercase letters), e.g. LKR',
  category: CAT_CLIENT_IMPORTANT,
});

check('NEXT_PUBLIC_CURRENCY_SYMBOL', {
  formatHint: 'non-empty string, e.g. Rs.',
  category: CAT_CLIENT_IMPORTANT,
});

// ── Feature Flag Variables ────────────────────────────────────────────────────

const CAT_FEATURE_FLAGS = 'Feature Flag Variables';

const featureFlags = [
  'NEXT_PUBLIC_ENABLE_ANALYTICS',
  'NEXT_PUBLIC_ENABLE_AI_FEATURES',
  'NEXT_PUBLIC_ENABLE_WEBSTORE',
  'NEXT_PUBLIC_ENABLE_POS',
  'NEXT_PUBLIC_ENABLE_OFFLINE',
  'NEXT_PUBLIC_DEBUG',
];

for (const flag of featureFlags) {
  check(flag, {
    optional: true,
    validate: isBooleanString,
    formatHint: '"true" or "false"',
    category: CAT_FEATURE_FLAGS,
  });
}

// ── Server-Only Variables ─────────────────────────────────────────────────────

const CAT_SERVER = 'Server-Only Variables';

check('API_BASE_URL', {
  required: true,
  validate: isValidURL,
  formatHint: 'valid HTTP(S) URL (use Docker service name in Docker)',
  category: CAT_SERVER,
});

check('NEXTAUTH_URL', {
  required: true,
  validate: isValidURL,
  formatHint: 'valid HTTP(S) URL',
  category: CAT_SERVER,
});

check('NEXTAUTH_SECRET', {
  requiredStrict: true,
  formatHint: 'non-empty secret string (required in production)',
  category: CAT_SERVER,
});

// ── Optional Variables ────────────────────────────────────────────────────────

const CAT_OPTIONAL = 'Optional Variables (validated if present)';

check('NEXT_PUBLIC_GA_TRACKING_ID', {
  optional: true,
  validate: isGA4TrackingID,
  formatHint: 'G-XXXXXXXXXX format',
  category: CAT_OPTIONAL,
});

check('NEXT_PUBLIC_SENTRY_DSN', {
  optional: true,
  validate: isValidURL,
  formatHint: 'valid URL (Sentry DSN)',
  category: CAT_OPTIONAL,
});

check('NEXT_PUBLIC_WS_URL', {
  optional: true,
  validate: isValidWSURL,
  formatHint: 'ws:// or wss:// URL',
  category: CAT_OPTIONAL,
});

check('STRIPE_SECRET_KEY', {
  optional: true,
  validate: isStripeSecretKey,
  formatHint: 'starts with sk_',
  category: CAT_OPTIONAL,
});

check('API_TIMEOUT', {
  optional: true,
  validate: isPositiveInteger,
  formatHint: 'positive integer (milliseconds)',
  category: CAT_OPTIONAL,
});

// ─── Output Results ───────────────────────────────────────────────────────────

/**
 * Prints items grouped by category.
 */
function printGrouped(items) {
  const grouped = {};
  for (const item of items) {
    const cat = item.category || 'Other';
    if (!grouped[cat]) grouped[cat] = [];
    grouped[cat].push(item);
  }
  for (const [category, entries] of Object.entries(grouped)) {
    console.log(`  ${colorize('cyan', category)}`);
    for (const entry of entries) {
      console.log(`    ${entry.message}`);
    }
    console.log('');
  }
}

// Print passed checks
if (results.passed.length > 0) {
  console.log(
    colorize('bold', '── Passed ──────────────────────────────────────────────')
  );
  console.log('');
  printGrouped(results.passed);
}

// Print warnings
if (results.warnings.length > 0) {
  console.log(
    colorize('bold', '── Warnings ────────────────────────────────────────────')
  );
  console.log('');
  printGrouped(results.warnings);
}

// Print errors
if (results.errors.length > 0) {
  console.log(
    colorize('bold', '── Errors ──────────────────────────────────────────────')
  );
  console.log('');
  printGrouped(results.errors);
}

// Print security warnings
if (results.securityWarnings.length > 0) {
  console.log(
    colorize('bold', '── Security Warnings ───────────────────────────────────')
  );
  console.log('');
  for (const warning of results.securityWarnings) {
    console.log(`    ${warning}`);
  }
  console.log('');
}

// ─── Summary ──────────────────────────────────────────────────────────────────

const totalChecks =
  results.passed.length + results.warnings.length + results.errors.length;
const hasErrors = results.errors.length > 0;

console.log(
  colorize('bold', '══════════════════════════════════════════════════════════')
);
console.log(
  colorize('bold', '  Summary') +
    colorize('dim', ` (${totalChecks} variables checked)`)
);
console.log(
  colorize('bold', '══════════════════════════════════════════════════════════')
);
console.log('');
console.log(
  `  ${icons.pass}  Passed:   ${colorize('green', String(results.passed.length))}`
);
console.log(
  `  ${icons.warn}  Warnings: ${colorize('yellow', String(results.warnings.length))}`
);
console.log(
  `  ${icons.fail}  Errors:   ${colorize('red', String(results.errors.length))}`
);

if (results.securityWarnings.length > 0) {
  console.log(
    `  ${icons.warn}  Security: ${colorize('yellow', String(results.securityWarnings.length))} potential secret(s) in NEXT_PUBLIC_ vars`
  );
}

console.log('');

if (hasErrors) {
  console.log(
    `  ${colorize('red', colorize('bold', 'FAILED'))} — Fix the errors above before proceeding.`
  );
  if (!isStrict) {
    console.log(
      `  ${colorize('dim', 'Tip: Run with --strict for production-level validation.')}`
    );
  }
  console.log('');
  process.exit(1);
} else if (results.warnings.length > 0) {
  console.log(
    `  ${colorize('yellow', colorize('bold', 'PASSED with warnings'))} — Consider setting the recommended variables.`
  );
  if (!isStrict) {
    console.log(
      `  ${colorize('dim', 'Tip: Run with --strict for production-level validation.')}`
    );
  }
  console.log('');
  process.exit(0);
} else {
  console.log(
    `  ${colorize('green', colorize('bold', 'ALL CHECKS PASSED'))} — Environment is fully configured.`
  );
  console.log('');
  process.exit(0);
}
