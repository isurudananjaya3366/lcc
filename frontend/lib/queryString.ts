/**
 * Query String Builder
 *
 * Utility for building URL query strings from JavaScript objects.
 * Supports nested objects, arrays, multiple serialization strategies,
 * and proper URL encoding.
 */

// ── Types ──────────────────────────────────────────────────────

export type ArrayFormat = 'repeat' | 'bracket' | 'comma' | 'index';
export type NestingFormat = 'dot' | 'bracket';

export interface QueryStringOptions {
  arrayFormat?: ArrayFormat;
  nestingFormat?: NestingFormat;
  skipNull?: boolean;
  skipEmptyString?: boolean;
  encode?: boolean;
  encodeValuesOnly?: boolean;
  maxDepth?: number;
}

const DEFAULT_OPTIONS: Required<QueryStringOptions> = {
  arrayFormat: 'repeat',
  nestingFormat: 'dot',
  skipNull: true,
  skipEmptyString: false,
  encode: true,
  encodeValuesOnly: false,
  maxDepth: 5,
};

// ── Core ───────────────────────────────────────────────────────

export function buildQueryString(
  params: Record<string, unknown>,
  options?: QueryStringOptions
): string {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const pairs: string[] = [];

  flattenParams(params, '', pairs, opts, 0);

  return pairs.join('&');
}

function flattenParams(
  obj: Record<string, unknown>,
  prefix: string,
  pairs: string[],
  opts: Required<QueryStringOptions>,
  depth: number
): void {
  if (depth > opts.maxDepth) return;

  for (const key of Object.keys(obj)) {
    const value = obj[key];
    const fullKey = prefix ? joinKey(prefix, key, opts.nestingFormat) : key;

    if (value === undefined) continue;
    if (value === null && opts.skipNull) continue;
    if (value === '' && opts.skipEmptyString) continue;

    if (value === null) {
      pairs.push(encodeEntry(fullKey, '', opts));
    } else if (Array.isArray(value)) {
      appendArray(fullKey, value, pairs, opts);
    } else if (value instanceof Date) {
      pairs.push(encodeEntry(fullKey, value.toISOString(), opts));
    } else if (typeof value === 'object') {
      flattenParams(
        value as Record<string, unknown>,
        fullKey,
        pairs,
        opts,
        depth + 1
      );
    } else {
      pairs.push(encodeEntry(fullKey, String(value), opts));
    }
  }
}

function joinKey(prefix: string, key: string, format: NestingFormat): string {
  return format === 'bracket' ? `${prefix}[${key}]` : `${prefix}.${key}`;
}

function appendArray(
  key: string,
  values: unknown[],
  pairs: string[],
  opts: Required<QueryStringOptions>
): void {
  if (values.length === 0) return;

  switch (opts.arrayFormat) {
    case 'comma':
      pairs.push(
        encodeEntry(key, values.map(String).join(','), opts)
      );
      break;
    case 'bracket':
      for (const v of values) {
        pairs.push(encodeEntry(`${key}[]`, String(v), opts));
      }
      break;
    case 'index':
      values.forEach((v, i) => {
        pairs.push(encodeEntry(`${key}[${i}]`, String(v), opts));
      });
      break;
    case 'repeat':
    default:
      for (const v of values) {
        pairs.push(encodeEntry(key, String(v), opts));
      }
      break;
  }
}

function encodeEntry(
  key: string,
  value: string,
  opts: Required<QueryStringOptions>
): string {
  if (!opts.encode) return `${key}=${value}`;
  if (opts.encodeValuesOnly) return `${key}=${encodeURIComponent(value)}`;
  return `${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
}

// ── Helpers ────────────────────────────────────────────────────

export function parseQueryString(qs: string): Record<string, string> {
  const result: Record<string, string> = {};
  const cleaned = qs.startsWith('?') ? qs.slice(1) : qs;
  if (!cleaned) return result;

  for (const pair of cleaned.split('&')) {
    const idx = pair.indexOf('=');
    if (idx === -1) {
      result[decodeURIComponent(pair)] = '';
    } else {
      const key = decodeURIComponent(pair.slice(0, idx));
      const value = decodeURIComponent(pair.slice(idx + 1));
      result[key] = value;
    }
  }
  return result;
}

export function appendQueryString(url: string, params: Record<string, unknown>, options?: QueryStringOptions): string {
  const qs = buildQueryString(params, options);
  if (!qs) return url;
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}${qs}`;
}

export function updateQueryString(
  url: string,
  updates: Record<string, unknown>,
  options?: QueryStringOptions
): string {
  const [base, existing] = url.split('?');
  const current = existing ? parseQueryString(existing) : {};
  const merged = { ...current, ...updates };
  const qs = buildQueryString(merged, options);
  return qs ? `${base}?${qs}` : base;
}
