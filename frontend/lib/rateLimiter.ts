/**
 * API Rate Limiter
 *
 * Client-side rate limiter with token bucket, sliding window,
 * and fixed window algorithms. Supports request queuing and
 * automatic retry with exponential backoff.
 */

// ── Types ──────────────────────────────────────────────────────

export type RateLimitStrategy = 'token' | 'sliding' | 'fixed';

export interface RateLimiterOptions {
  maxRequests?: number;
  windowMs?: number;
  strategy?: RateLimitStrategy;
  queueEnabled?: boolean;
  maxQueueSize?: number;
  throwOnLimit?: boolean;
}

export interface RateLimitRetryOptions {
  maxRetries?: number;
  retryDelay?: number;
  retryBackoff?: number;
  retryableStatuses?: number[];
  retryOnTimeout?: boolean;
}

interface QueuedRequest<T> {
  execute: () => Promise<T>;
  resolve: (value: T) => void;
  reject: (reason: unknown) => void;
}

const DEFAULT_OPTIONS: Required<RateLimiterOptions> = {
  maxRequests: 10,
  windowMs: 60_000,
  strategy: 'token',
  queueEnabled: true,
  maxQueueSize: 50,
  throwOnLimit: false,
};

const DEFAULT_RETRY: Required<RateLimitRetryOptions> = {
  maxRetries: 3,
  retryDelay: 1000,
  retryBackoff: 2,
  retryableStatuses: [429, 500, 502, 503, 504],
  retryOnTimeout: true,
};

// ── Rate Limiter ───────────────────────────────────────────────

export class RateLimiter {
  private options: Required<RateLimiterOptions>;
  private retryOpts: Required<RateLimitRetryOptions>;

  // Token bucket state
  private tokens: number;
  private lastRefill: number;

  // Sliding window state
  private timestamps: number[] = [];

  // Fixed window state
  private windowStart: number;
  private windowCount: number;

  // Queue
  private queue: QueuedRequest<unknown>[] = [];
  private processing = false;

  constructor(options?: RateLimiterOptions, retryOptions?: RateLimitRetryOptions) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.retryOpts = { ...DEFAULT_RETRY, ...retryOptions };

    this.tokens = this.options.maxRequests;
    this.lastRefill = Date.now();
    this.windowStart = Date.now();
    this.windowCount = 0;
  }

  // ── Execute ──────────────────────────────────────────────────

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.canProceed()) {
      this.recordRequest();
      return fn();
    }

    if (this.options.queueEnabled) {
      if (this.queue.length >= this.options.maxQueueSize) {
        throw new Error('Rate limit queue is full');
      }
      return this.enqueue(fn);
    }

    if (this.options.throwOnLimit) {
      throw new Error('Rate limit exceeded');
    }

    // Wait for next available slot
    const wait = this.getTimeUntilReset();
    await this.delay(wait);
    this.recordRequest();
    return fn();
  }

  async executeWithRetry<T>(
    fn: () => Promise<T>,
    retryOptions?: RateLimitRetryOptions
  ): Promise<T> {
    const opts = { ...this.retryOpts, ...retryOptions };
    let lastError: unknown;

    for (let attempt = 0; attempt <= opts.maxRetries; attempt++) {
      try {
        return await this.execute(fn);
      } catch (err: unknown) {
        lastError = err;
        const isRetryable = this.isRetryableError(err, opts);
        if (!isRetryable || attempt === opts.maxRetries) break;

        const retryAfter = this.getRetryAfterMs(err);
        const backoff = retryAfter ?? opts.retryDelay * Math.pow(opts.retryBackoff, attempt);
        await this.delay(backoff);
      }
    }

    throw lastError;
  }

  // ── Algorithm Checks ─────────────────────────────────────────

  private canProceed(): boolean {
    switch (this.options.strategy) {
      case 'token':
        return this.canProceedToken();
      case 'sliding':
        return this.canProceedSliding();
      case 'fixed':
        return this.canProceedFixed();
      default:
        return this.canProceedToken();
    }
  }

  private canProceedToken(): boolean {
    this.refillTokens();
    return this.tokens > 0;
  }

  private canProceedSliding(): boolean {
    const now = Date.now();
    this.timestamps = this.timestamps.filter((t) => now - t < this.options.windowMs);
    return this.timestamps.length < this.options.maxRequests;
  }

  private canProceedFixed(): boolean {
    const now = Date.now();
    if (now - this.windowStart >= this.options.windowMs) {
      this.windowStart = now;
      this.windowCount = 0;
    }
    return this.windowCount < this.options.maxRequests;
  }

  private recordRequest(): void {
    switch (this.options.strategy) {
      case 'token':
        this.tokens--;
        break;
      case 'sliding':
        this.timestamps.push(Date.now());
        break;
      case 'fixed':
        this.windowCount++;
        break;
    }
  }

  private refillTokens(): void {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    const refillRate = this.options.maxRequests / this.options.windowMs;
    const tokensToAdd = elapsed * refillRate;
    this.tokens = Math.min(this.options.maxRequests, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }

  // ── Queue ────────────────────────────────────────────────────

  private enqueue<T>(fn: () => Promise<T>): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      this.queue.push({
        execute: fn as () => Promise<unknown>,
        resolve: resolve as (v: unknown) => void,
        reject,
      });
      this.processQueue();
    });
  }

  private async processQueue(): Promise<void> {
    if (this.processing || this.queue.length === 0) return;
    this.processing = true;

    while (this.queue.length > 0) {
      if (!this.canProceed()) {
        const wait = this.getTimeUntilReset();
        await this.delay(wait);
        continue;
      }

      const item = this.queue.shift();
      if (!item) break;

      this.recordRequest();
      try {
        const result = await item.execute();
        item.resolve(result);
      } catch (err) {
        item.reject(err);
      }
    }

    this.processing = false;
  }

  // ── Retry Helpers ────────────────────────────────────────────

  private isRetryableError(err: unknown, opts: Required<RateLimitRetryOptions>): boolean {
    if (err && typeof err === 'object') {
      const status = (err as { status?: number }).status;
      if (status && opts.retryableStatuses.includes(status)) return true;
      const code = (err as { code?: string }).code;
      if (code === 'ECONNABORTED' && opts.retryOnTimeout) return true;
      if (code === 'ERR_NETWORK') return true;
    }
    return false;
  }

  private getRetryAfterMs(err: unknown): number | null {
    if (err && typeof err === 'object') {
      const headers = (err as { headers?: Record<string, string> }).headers;
      const retryAfter = headers?.['retry-after'];
      if (retryAfter) {
        const seconds = parseInt(retryAfter, 10);
        return isNaN(seconds) ? null : seconds * 1000;
      }
    }
    return null;
  }

  // ── Status ───────────────────────────────────────────────────

  getRemainingRequests(): number {
    switch (this.options.strategy) {
      case 'token':
        this.refillTokens();
        return Math.floor(this.tokens);
      case 'sliding': {
        const now = Date.now();
        const active = this.timestamps.filter((t) => now - t < this.options.windowMs).length;
        return this.options.maxRequests - active;
      }
      case 'fixed': {
        const now = Date.now();
        if (now - this.windowStart >= this.options.windowMs) return this.options.maxRequests;
        return this.options.maxRequests - this.windowCount;
      }
      default:
        return 0;
    }
  }

  getTimeUntilReset(): number {
    switch (this.options.strategy) {
      case 'token': {
        if (this.tokens > 0) return 0;
        return Math.ceil(1 / (this.options.maxRequests / this.options.windowMs));
      }
      case 'sliding': {
        if (this.timestamps.length < this.options.maxRequests) return 0;
        const oldest = this.timestamps[0];
        return Math.max(0, this.options.windowMs - (Date.now() - (oldest ?? Date.now())));
      }
      case 'fixed':
        return Math.max(0, this.options.windowMs - (Date.now() - this.windowStart));
      default:
        return 0;
    }
  }

  getQueueLength(): number {
    return this.queue.length;
  }

  clearQueue(): void {
    for (const item of this.queue) {
      item.reject(new Error('Queue cleared'));
    }
    this.queue = [];
  }

  reset(): void {
    this.tokens = this.options.maxRequests;
    this.lastRefill = Date.now();
    this.timestamps = [];
    this.windowStart = Date.now();
    this.windowCount = 0;
    this.clearQueue();
  }

  // ── Utility ──────────────────────────────────────────────────

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
