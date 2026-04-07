// ================================================================
// Background Sync Manager — Task 33
// ================================================================
// Registers and manages Background Sync / Periodic Sync tags
// and provides a BroadcastChannel for sync status messages.
// ================================================================

// ── Sync tags ──────────────────────────────────────────────────

export const SYNC_TAGS = {
  TRANSACTIONS: 'sync-transactions',
  CACHE_REFRESH: 'sync-cache-refresh',
} as const;

// ── Broadcast channel ──────────────────────────────────────────

const CHANNEL_NAME = 'pos-sync-channel';

export type SyncMessageType =
  | 'sync-started'
  | 'sync-progress'
  | 'sync-complete'
  | 'sync-failed';

export interface SyncMessage {
  type: SyncMessageType;
  tag: string;
  payload?: unknown;
  timestamp: string;
}

// ── Queue config ───────────────────────────────────────────────

export const SYNC_QUEUE_CONFIG = {
  MAX_RETRIES: 5,
  INITIAL_RETRY_DELAY_MS: 60_000, // 1 minute
  MAX_RETRY_DELAY_MS: 3_600_000, // 1 hour
  BACKOFF_MULTIPLIER: 2,
} as const;

// ── Service ────────────────────────────────────────────────────

class SyncManager {
  private channel: BroadcastChannel | null = null;

  private getChannel(): BroadcastChannel {
    if (!this.channel && typeof BroadcastChannel !== 'undefined') {
      this.channel = new BroadcastChannel(CHANNEL_NAME);
    }
    return this.channel!;
  }

  // ── Feature detection ────────────────────────────────────────

  isBackgroundSyncSupported(): boolean {
    return (
      typeof navigator !== 'undefined' &&
      'serviceWorker' in navigator &&
      'SyncManager' in globalThis
    );
  }

  isPeriodicSyncSupported(): boolean {
    return (
      typeof navigator !== 'undefined' &&
      'serviceWorker' in navigator &&
      'PeriodicSyncManager' in globalThis
    );
  }

  // ── Registration ─────────────────────────────────────────────

  async registerBackgroundSync(tag: string): Promise<void> {
    if (!this.isBackgroundSyncSupported()) {
      console.warn('[SyncManager] Background Sync not supported');
      return;
    }
    const registration = await navigator.serviceWorker.ready;
    await (
      registration as ServiceWorkerRegistration & {
        sync: { register(tag: string): Promise<void> };
      }
    ).sync.register(tag);
  }

  async registerTransactionSync(): Promise<void> {
    await this.registerBackgroundSync(SYNC_TAGS.TRANSACTIONS);
  }

  async triggerManualSync(tag: string): Promise<void> {
    // Post a message to the active SW asking it to run the sync
    const registration = await navigator.serviceWorker.ready;
    registration.active?.postMessage({ type: 'MANUAL_SYNC', tag });
  }

  // ── Broadcasting ─────────────────────────────────────────────

  broadcastSyncStatus(
    type: SyncMessageType,
    tag: string,
    payload?: unknown
  ): void {
    const channel = this.getChannel();
    if (!channel) return;
    const message: SyncMessage = {
      type,
      tag,
      payload,
      timestamp: new Date().toISOString(),
    };
    channel.postMessage(message);
  }

  /** Listen for sync status messages from the service worker. */
  onSyncMessage(callback: (msg: SyncMessage) => void): () => void {
    const channel = this.getChannel();
    if (!channel) return () => {};
    const handler = (event: MessageEvent) =>
      callback(event.data as SyncMessage);
    channel.addEventListener('message', handler);
    return () => channel.removeEventListener('message', handler);
  }

  /** Close the broadcast channel. */
  dispose(): void {
    this.channel?.close();
    this.channel = null;
  }
}

export const syncManager = new SyncManager();
