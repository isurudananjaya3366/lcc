// ================================================================
// Connection Monitor — Tasks 53, 57-58
// ================================================================
// Detects and monitors internet connectivity with multiple
// strategies: navigator.onLine, server ping, latency measurement,
// visibility/focus re-checks, and debounced change events.
// ================================================================

import {
  ConnectionQuality,
  HEALTH_PING_ENDPOINT,
  PING_TIMEOUT,
  PING_RETRY_COUNT,
  PING_RETRY_INTERVAL,
  LATENCY_THRESHOLD_SLOW,
  LATENCY_THRESHOLD_NORMAL,
  CONNECTION_DEBOUNCE_DELAY,
  CONNECTION_CHECK_INTERVAL_OFFLINE,
  CONNECTION_CHECK_INTERVAL_ONLINE,
  type ConnectionChangeEvent,
} from './sync-types';

type ConnectionChangeCallback = (event: ConnectionChangeEvent) => void;

export class ConnectionMonitor {
  private online = typeof navigator !== 'undefined' ? navigator.onLine : true;
  private previouslyOnline = this.online;
  private lastConnectionCheckTime = 0;
  private lastSuccessfulConnectionTime = 0;
  private quality: ConnectionQuality = ConnectionQuality.NORMAL;
  private checkTimer?: ReturnType<typeof setInterval>;
  private debounceTimer?: ReturnType<typeof setTimeout>;
  private callbacks: ConnectionChangeCallback[] = [];
  private boundOnline = this.handleOnlineEvent.bind(this);
  private boundOffline = this.handleOfflineEvent.bind(this);
  private boundVisibility = this.handleVisibilityChange.bind(this);
  private boundFocus = this.handleFocus.bind(this);
  private destroyed = false;

  // ---- Public API ----

  async checkConnection(): Promise<boolean> {
    this.lastConnectionCheckTime = Date.now();

    // Layer 1: navigator.onLine
    if (typeof navigator !== 'undefined' && !navigator.onLine) {
      this.updateStatus(false);
      return false;
    }

    // Layer 2: ping the server
    const result = await this.pingServer();
    this.updateStatus(result);
    return result;
  }

  startMonitoring(interval?: number): void {
    this.setupEventListeners();
    const ms =
      interval ??
      (this.online
        ? CONNECTION_CHECK_INTERVAL_ONLINE
        : CONNECTION_CHECK_INTERVAL_OFFLINE);
    this.checkTimer = setInterval(() => this.checkConnection(), ms);
  }

  stopMonitoring(): void {
    this.removeEventListeners();
    if (this.checkTimer) {
      clearInterval(this.checkTimer);
      this.checkTimer = undefined;
    }
  }

  getIsOnline(): boolean {
    return this.online;
  }

  getConnectionQuality(): ConnectionQuality {
    return this.quality;
  }

  getLastSuccessfulConnectionTime(): number {
    return this.lastSuccessfulConnectionTime;
  }

  onConnectionChange(callback: ConnectionChangeCallback): () => void {
    this.callbacks.push(callback);
    return () => {
      this.callbacks = this.callbacks.filter((c) => c !== callback);
    };
  }

  destroy(): void {
    this.destroyed = true;
    this.stopMonitoring();
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    this.callbacks = [];
  }

  // ---- Private Helpers ----

  private updateStatus(isOnline: boolean): void {
    const changed = isOnline !== this.online;
    this.previouslyOnline = this.online;
    this.online = isOnline;
    if (isOnline) this.lastSuccessfulConnectionTime = Date.now();
    if (changed) this.debouncedNotify();
  }

  private debouncedNotify(): void {
    if (this.debounceTimer) clearTimeout(this.debounceTimer);
    this.debounceTimer = setTimeout(() => {
      if (this.destroyed) return;
      this.assessConnectionQuality().then((q) => {
        this.quality = q;
        const event: ConnectionChangeEvent = {
          online: this.online,
          previouslyOnline: this.previouslyOnline,
          timestamp: Date.now(),
          quality: this.quality,
          verified: true,
        };
        for (const cb of this.callbacks) {
          try {
            cb(event);
          } catch {
            /* swallow callback errors */
          }
        }
      });
    }, CONNECTION_DEBOUNCE_DELAY);
  }

  private async pingServer(): Promise<boolean> {
    for (let i = 0; i <= PING_RETRY_COUNT; i++) {
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), PING_TIMEOUT);
        const start = performance.now();
        const res = await fetch(HEALTH_PING_ENDPOINT, {
          method: 'HEAD',
          signal: controller.signal,
          cache: 'no-store',
        });
        clearTimeout(timer);
        if (res.ok) {
          const latency = performance.now() - start;
          this.quality = this.latencyToQuality(latency);
          return true;
        }
      } catch {
        if (i < PING_RETRY_COUNT) {
          await new Promise((r) => setTimeout(r, PING_RETRY_INTERVAL));
        }
      }
    }
    return false;
  }

  private async assessConnectionQuality(): Promise<ConnectionQuality> {
    if (!this.online) return ConnectionQuality.OFFLINE;
    try {
      const latency = await this.measureLatency();
      return this.latencyToQuality(latency);
    } catch {
      return ConnectionQuality.NORMAL;
    }
  }

  private async measureLatency(): Promise<number> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), PING_TIMEOUT);
    const start = performance.now();
    await fetch(HEALTH_PING_ENDPOINT, {
      method: 'HEAD',
      signal: controller.signal,
      cache: 'no-store',
    });
    clearTimeout(timer);
    return performance.now() - start;
  }

  private latencyToQuality(latency: number): ConnectionQuality {
    if (latency > LATENCY_THRESHOLD_SLOW) return ConnectionQuality.SLOW;
    if (latency > LATENCY_THRESHOLD_NORMAL) return ConnectionQuality.NORMAL;
    return ConnectionQuality.FAST;
  }

  // ---- Browser Event Listeners ----

  private setupEventListeners(): void {
    if (typeof window === 'undefined') return;
    window.addEventListener('online', this.boundOnline);
    window.addEventListener('offline', this.boundOffline);
    document.addEventListener('visibilitychange', this.boundVisibility);
    window.addEventListener('focus', this.boundFocus);
  }

  private removeEventListeners(): void {
    if (typeof window === 'undefined') return;
    window.removeEventListener('online', this.boundOnline);
    window.removeEventListener('offline', this.boundOffline);
    document.removeEventListener('visibilitychange', this.boundVisibility);
    window.removeEventListener('focus', this.boundFocus);
  }

  private handleOnlineEvent(): void {
    this.checkConnection();
  }

  private handleOfflineEvent(): void {
    this.updateStatus(false);
  }

  private handleVisibilityChange(): void {
    if (document.visibilityState === 'visible') this.checkConnection();
  }

  private handleFocus(): void {
    this.checkConnection();
  }
}

export const connectionMonitor = new ConnectionMonitor();
