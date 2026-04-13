/**
 * URL Path Builder
 *
 * Utility for constructing URL paths with dynamic parameter replacement,
 * query string appending, and base URL prepending.
 */

import { buildQueryString, type QueryStringOptions } from './queryString';

// ── Types ──────────────────────────────────────────────────────

export interface UrlBuilderOptions {
  baseUrl?: string;
  pathParams?: Record<string, string | number>;
  queryParams?: Record<string, unknown>;
  trailingSlash?: boolean | 'preserve';
  validate?: boolean;
  encodePathParams?: boolean;
  queryStringOptions?: QueryStringOptions;
}

// ── Core ───────────────────────────────────────────────────────

export function buildUrl(
  template: string,
  options: UrlBuilderOptions = {}
): string {
  const {
    baseUrl,
    pathParams = {},
    queryParams,
    trailingSlash = 'preserve',
    validate = true,
    encodePathParams = true,
    queryStringOptions,
  } = options;

  // Replace path parameters (:param and {param} syntax)
  let path = template.replace(
    /[:]{1}([a-zA-Z_]\w*)|[{]([a-zA-Z_]\w*)[}]/g,
    (_match, colonParam, braceParam) => {
      const paramName = colonParam || braceParam;
      const value = pathParams[paramName];
      if (value === undefined || value === null) {
        if (validate) {
          throw new Error(`Missing required path parameter: ${paramName}`);
        }
        return _match;
      }
      const str = String(value);
      return encodePathParams ? encodeURIComponent(str) : str;
    }
  );

  // Normalize path: collapse multiple slashes, remove empty segments
  path = path
    .split('/')
    .filter((seg, i) => i === 0 || seg !== '')
    .join('/');

  // Prepend base URL
  if (baseUrl) {
    const base = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    const rel = path.startsWith('/') ? path : `/${path}`;
    path = `${base}${rel}`;
  }

  // Trailing slash
  if (trailingSlash === true && !path.endsWith('/')) {
    path += '/';
  } else if (trailingSlash === false && path.endsWith('/') && path !== '/') {
    path = path.slice(0, -1);
  }

  // Query string
  if (queryParams && Object.keys(queryParams).length > 0) {
    const qs = buildQueryString(queryParams, queryStringOptions);
    if (qs) {
      const separator = path.includes('?') ? '&' : '?';
      path = `${path}${separator}${qs}`;
    }
  }

  return path;
}

// ── Helpers ────────────────────────────────────────────────────

export function buildApiUrl(
  template: string,
  options: Omit<UrlBuilderOptions, 'baseUrl'> = {}
): string {
  const baseUrl =
    typeof process !== 'undefined'
      ? process.env.NEXT_PUBLIC_API_URL || ''
      : '';
  return buildUrl(template, { ...options, baseUrl });
}

export function buildResourceUrl(
  resource: string,
  id?: string | number,
  options: Omit<UrlBuilderOptions, 'pathParams'> = {}
): string {
  const template = id !== undefined ? `/${resource}/${id}` : `/${resource}`;
  return buildUrl(template, options);
}

export function isAbsoluteUrl(url: string): boolean {
  return /^https?:\/\//i.test(url);
}
