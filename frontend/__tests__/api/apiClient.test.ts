/**
 * API Client Tests
 *
 * Comprehensive tests for apiClient, services, utilities,
 * cache, rate limiter, and error handling.
 */

import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { server } from '@/mocks/server';

// ── MSW Lifecycle ──────────────────────────────────────────────

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// ── Query String Builder ───────────────────────────────────────

describe('buildQueryString', () => {
  // Dynamically import to keep tests isolated
  let buildQueryString: typeof import('@/lib/queryString').buildQueryString;
  let parseQueryString: typeof import('@/lib/queryString').parseQueryString;
  let appendQueryString: typeof import('@/lib/queryString').appendQueryString;

  beforeAll(async () => {
    const mod = await import('@/lib/queryString');
    buildQueryString = mod.buildQueryString;
    parseQueryString = mod.parseQueryString;
    appendQueryString = mod.appendQueryString;
  });

  it('should build simple query string', () => {
    const result = buildQueryString({ search: 'laptop', page: 1, limit: 20 });
    expect(result).toContain('search=laptop');
    expect(result).toContain('page=1');
    expect(result).toContain('limit=20');
  });

  it('should skip undefined values', () => {
    const result = buildQueryString({ search: 'laptop', page: undefined });
    expect(result).toBe('search=laptop');
  });

  it('should skip null values by default', () => {
    const result = buildQueryString({ search: 'laptop', category: null });
    expect(result).toBe('search=laptop');
  });

  it('should handle array with repeat format', () => {
    const result = buildQueryString(
      { ids: [1, 2, 3] },
      { arrayFormat: 'repeat' }
    );
    expect(result).toBe('ids=1&ids=2&ids=3');
  });

  it('should handle array with comma format', () => {
    const result = buildQueryString(
      { ids: [1, 2, 3] },
      { arrayFormat: 'comma' }
    );
    expect(result).toBe('ids=1%2C2%2C3');
  });

  it('should handle nested objects with dot notation', () => {
    const result = buildQueryString(
      { filter: { category: 'electronics' } },
      { nestingFormat: 'dot', encode: false }
    );
    expect(result).toBe('filter.category=electronics');
  });

  it('should parse query string back to object', () => {
    const result = parseQueryString('search=laptop&page=1');
    expect(result).toEqual({ search: 'laptop', page: '1' });
  });

  it('should append query string to URL', () => {
    const url = appendQueryString('/api/products', { page: 1 });
    expect(url).toContain('/api/products?');
    expect(url).toContain('page=1');
  });
});

// ── URL Builder ────────────────────────────────────────────────

describe('buildUrl', () => {
  let buildUrl: typeof import('@/lib/urlBuilder').buildUrl;
  let isAbsoluteUrl: typeof import('@/lib/urlBuilder').isAbsoluteUrl;

  beforeAll(async () => {
    const mod = await import('@/lib/urlBuilder');
    buildUrl = mod.buildUrl;
    isAbsoluteUrl = mod.isAbsoluteUrl;
  });

  it('should replace colon-style path params', () => {
    const result = buildUrl('/users/:id', { pathParams: { id: 123 } });
    expect(result).toBe('/users/123');
  });

  it('should replace brace-style path params', () => {
    const result = buildUrl('/users/{id}', { pathParams: { id: 123 } });
    expect(result).toBe('/users/123');
  });

  it('should throw on missing required param', () => {
    expect(() => buildUrl('/users/:id', { validate: true })).toThrow(
      'Missing required path parameter: id'
    );
  });

  it('should prepend base URL', () => {
    const result = buildUrl('/users/1', {
      baseUrl: 'https://api.example.com',
    });
    expect(result).toBe('https://api.example.com/users/1');
  });

  it('should append query params', () => {
    const result = buildUrl('/users', { queryParams: { page: 1 } });
    expect(result).toContain('page=1');
  });

  it('should detect absolute URLs', () => {
    expect(isAbsoluteUrl('https://example.com')).toBe(true);
    expect(isAbsoluteUrl('/api/users')).toBe(false);
  });
});

// ── FormData Builder ───────────────────────────────────────────

describe('buildFormData', () => {
  let buildFormData: typeof import('@/lib/formDataBuilder').buildFormData;
  let formDataToObject: typeof import('@/lib/formDataBuilder').formDataToObject;

  beforeAll(async () => {
    const mod = await import('@/lib/formDataBuilder');
    buildFormData = mod.buildFormData;
    formDataToObject = mod.formDataToObject;
  });

  it('should build FormData from simple object', () => {
    const fd = buildFormData({ name: 'John', age: 30 });
    expect(fd.get('name')).toBe('John');
    expect(fd.get('age')).toBe('30');
  });

  it('should skip undefined values', () => {
    const fd = buildFormData({ name: 'John', extra: undefined });
    const obj = formDataToObject(fd);
    expect(obj).not.toHaveProperty('extra');
  });

  it('should convert booleans to strings', () => {
    const fd = buildFormData({ active: true });
    expect(fd.get('active')).toBe('true');
  });

  it('should handle Date as ISO string', () => {
    const date = new Date('2025-01-01');
    const fd = buildFormData({ date });
    expect(fd.get('date')).toBe(date.toISOString());
  });
});

// ── File Helpers ───────────────────────────────────────────────

describe('fileHelpers', () => {
  let validateFile: typeof import('@/lib/fileHelpers').validateFile;
  let getFileExtension: typeof import('@/lib/fileHelpers').getFileExtension;
  let formatFileSize: typeof import('@/lib/fileHelpers').formatFileSize;
  let getMimeType: typeof import('@/lib/fileHelpers').getMimeType;
  let getFilenameFromHeader: typeof import('@/lib/fileHelpers').getFilenameFromHeader;

  beforeAll(async () => {
    const mod = await import('@/lib/fileHelpers');
    validateFile = mod.validateFile;
    getFileExtension = mod.getFileExtension;
    formatFileSize = mod.formatFileSize;
    getMimeType = mod.getMimeType;
    getFilenameFromHeader = mod.getFilenameFromHeader;
  });

  it('should validate file size', () => {
    const file = new File(['x'.repeat(1000)], 'test.txt', { type: 'text/plain' });
    const result = validateFile(file, { maxSize: 500 });
    expect(result.valid).toBe(false);
    expect(result.errors[0]).toContain('exceeds maximum');
  });

  it('should validate file type', () => {
    const file = new File([''], 'test.exe', { type: 'application/x-msdownload' });
    const result = validateFile(file, { allowedTypes: ['image/jpeg', 'image/png'] });
    expect(result.valid).toBe(false);
  });

  it('should pass valid file', () => {
    const file = new File(['x'], 'test.jpg', { type: 'image/jpeg' });
    const result = validateFile(file, {
      maxSize: 5_000_000,
      allowedTypes: ['image/jpeg'],
    });
    expect(result.valid).toBe(true);
  });

  it('should extract file extension', () => {
    expect(getFileExtension('report.pdf')).toBe('.pdf');
    expect(getFileExtension('noext')).toBe('');
  });

  it('should format file size', () => {
    expect(formatFileSize(0)).toBe('0 B');
    expect(formatFileSize(1024)).toBe('1.0 KB');
    expect(formatFileSize(1_048_576)).toBe('1.0 MB');
  });

  it('should get MIME type from filename', () => {
    expect(getMimeType('file.pdf')).toBe('application/pdf');
    expect(getMimeType('file.xyz')).toBe('application/octet-stream');
  });

  it('should extract filename from Content-Disposition', () => {
    expect(getFilenameFromHeader('attachment; filename="report.pdf"')).toBe('report.pdf');
    expect(getFilenameFromHeader(null)).toBeNull();
  });
});

// ── API Cache ──────────────────────────────────────────────────

describe('ApiCache', () => {
  let ApiCache: typeof import('@/lib/apiCache').ApiCache;

  beforeAll(async () => {
    const mod = await import('@/lib/apiCache');
    ApiCache = mod.ApiCache;
  });

  it('should cache and retrieve values', () => {
    const cache = new ApiCache();
    cache.set('key1', { name: 'test' });
    expect(cache.get('key1')).toEqual({ name: 'test' });
  });

  it('should return null for missing keys', () => {
    const cache = new ApiCache();
    expect(cache.get('missing')).toBeNull();
  });

  it('should expire entries after maxAge', async () => {
    const cache = new ApiCache({ maxAge: 50 });
    cache.set('short', 'data');
    expect(cache.get('short')).toBe('data');
    await new Promise((r) => setTimeout(r, 80));
    expect(cache.get('short')).toBeNull();
  });

  it('should evict LRU when maxSize exceeded', () => {
    const cache = new ApiCache({ maxSize: 2 });
    cache.set('a', 1);
    cache.set('b', 2);
    cache.get('a'); // access 'a' so 'b' is LRU
    cache.set('c', 3);
    expect(cache.get('b')).toBeNull();
    expect(cache.get('a')).toBe(1);
    expect(cache.get('c')).toBe(3);
  });

  it('should invalidate by pattern', () => {
    const cache = new ApiCache();
    cache.set('GET:/api/users', []);
    cache.set('GET:/api/users/1', {});
    cache.set('GET:/api/products', []);
    const count = cache.invalidatePattern(/\/api\/users/);
    expect(count).toBe(2);
    expect(cache.get('GET:/api/products')).toEqual([]);
  });

  it('should track stats', () => {
    const cache = new ApiCache();
    cache.set('k', 1);
    cache.get('k'); // hit
    cache.get('miss'); // miss
    const stats = cache.getStats();
    expect(stats.hits).toBe(1);
    expect(stats.misses).toBe(1);
    expect(stats.size).toBe(1);
  });

  it('should generate consistent cache keys', () => {
    const key1 = ApiCache.generateKey('GET', '/api/users', { page: 1, sort: 'name' });
    const key2 = ApiCache.generateKey('GET', '/api/users', { sort: 'name', page: 1 });
    expect(key1).toBe(key2);
  });
});

// ── Rate Limiter ───────────────────────────────────────────────

describe('RateLimiter', () => {
  let RateLimiter: typeof import('@/lib/rateLimiter').RateLimiter;

  beforeAll(async () => {
    const mod = await import('@/lib/rateLimiter');
    RateLimiter = mod.RateLimiter;
  });

  it('should allow requests within limit', async () => {
    const limiter = new RateLimiter({ maxRequests: 3, windowMs: 1000, strategy: 'sliding' });
    const results: number[] = [];
    for (let i = 0; i < 3; i++) {
      await limiter.execute(async () => results.push(i));
    }
    expect(results).toEqual([0, 1, 2]);
  });

  it('should report remaining requests', () => {
    const limiter = new RateLimiter({ maxRequests: 5, windowMs: 60000, strategy: 'token' });
    expect(limiter.getRemainingRequests()).toBe(5);
  });

  it('should throw when queue is full', async () => {
    const limiter = new RateLimiter({
      maxRequests: 1,
      windowMs: 60000,
      strategy: 'fixed',
      queueEnabled: true,
      maxQueueSize: 0,
    });
    // Consume the single request
    await limiter.execute(async () => 'ok');
    await expect(
      limiter.execute(async () => 'overflow')
    ).rejects.toThrow('Rate limit queue is full');
  });

  it('should reset state', () => {
    const limiter = new RateLimiter({ maxRequests: 5, strategy: 'token' });
    limiter.reset();
    expect(limiter.getRemainingRequests()).toBe(5);
    expect(limiter.getQueueLength()).toBe(0);
  });
});

// ── API Error ──────────────────────────────────────────────────

describe('ApiException', () => {
  let ApiException: typeof import('@/lib/apiError').ApiException;
  let isRetryable: typeof import('@/lib/apiError').isRetryable;
  let getErrorMessage: typeof import('@/lib/apiError').getErrorMessage;

  beforeAll(async () => {
    const mod = await import('@/lib/apiError');
    ApiException = mod.ApiException;
    isRetryable = mod.isRetryable;
    getErrorMessage = mod.getErrorMessage;
  });

  it('should create error with properties', () => {
    const err = new ApiException('Not Found', { code: 'NOT_FOUND', status: 404 });
    expect(err.message).toBe('Not Found');
    expect(err.code).toBe('NOT_FOUND');
    expect(err.status).toBe(404);
  });

  it('should serialize to JSON', () => {
    const err = new ApiException('fail', { code: 'ERR', status: 500 });
    const json = err.toJSON();
    expect(json.message).toBe('fail');
    expect(json.code).toBe('ERR');
    expect(json.status).toBe(500);
  });

  it('should identify retryable errors', () => {
    const err500 = new ApiException('Server Error', { code: 'SERVER_ERROR', status: 500 });
    const err404 = new ApiException('Not Found', { code: 'NOT_FOUND', status: 404 });
    expect(isRetryable(err500)).toBe(true);
    expect(isRetryable(err404)).toBe(false);
  });

  it('should return user-friendly messages', () => {
    const err = new ApiException('err', { code: 'ERR', status: 401 });
    const msg = getErrorMessage(err);
    expect(typeof msg).toBe('string');
    expect(msg.length).toBeGreaterThan(0);
  });
});
