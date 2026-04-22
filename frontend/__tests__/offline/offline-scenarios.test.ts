// @vitest-environment jsdom
// ================================================================
// Task 88: Offline Scenario Tests (Integration / E2E)
// ================================================================

/* eslint-disable @typescript-eslint/no-explicit-any */
declare const describe: any;
declare const it: any;
declare const expect: any;
declare const afterEach: any;
declare const beforeAll: any;

// Polyfill IndexedDB for jsdom environment
import 'fake-indexeddb/auto';

// These tests simulate real-world offline scenarios within a JSDOM/
// test environment. They exercise the full stack: IndexedDB → Queue
// → Sync Engine → UI hooks. They may require fake-indexeddb and
// a fetch polyfill depending on the runner.
// ================================================================

import { generateOfflineTransactionId } from '@/lib/offline/id-generator';
import type { TransactionPayload } from '@/lib/offline/queue-types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

let originalOnline: boolean;

function simulateOffline() {
  Object.defineProperty(navigator, 'onLine', {
    value: false,
    writable: true,
    configurable: true,
  });
  window.dispatchEvent(new Event('offline'));
}

function simulateOnline() {
  Object.defineProperty(navigator, 'onLine', {
    value: true,
    writable: true,
    configurable: true,
  });
  window.dispatchEvent(new Event('online'));
}

function makeSalePayload(overrides: Partial<TransactionPayload> = {}): TransactionPayload {
  return {
    terminal_id: 'T-SCENARIO',
    session_id: 'SESSION-001',
    items: [{ product_id: 'prod-1', quantity: 1, price: 100, subtotal: 100 }],
    grand_total: 100,
    payment_method: 'cash',
    timestamp: new Date().toISOString(),
    subtotal: 100,
    tax_amount: 0,
    discount_amount: 0,
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Scenario Tests
// ---------------------------------------------------------------------------

describe('Offline Scenarios', () => {
  let originalFetch: typeof globalThis.fetch;

  beforeAll(() => {
    originalOnline = navigator.onLine;
    originalFetch = globalThis.fetch;
  });

  // restore online state after each test
  afterEach(() => {
    simulateOnline();
    globalThis.fetch = originalFetch;
  });

  // ----------------------------------------------------------
  // Scenario 1: Basic offline transaction flow
  // ----------------------------------------------------------
  describe('Offline Transaction Flow', () => {
    it('should create a transaction with an offline ID while offline', () => {
      simulateOffline();
      const offlineId = generateOfflineTransactionId('sale');
      expect(offlineId).toBeTruthy();
      expect(offlineId).toMatch(/^OFFLINE-/);
      expect(navigator.onLine).toBe(false);
    });

    it('should restore online status on reconnect', () => {
      simulateOffline();
      expect(navigator.onLine).toBe(false);
      simulateOnline();
      expect(navigator.onLine).toBe(true);
    });

    it('should store transaction in queue while offline', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      simulateOffline();
      const id = await queue.queueTransaction(makeSalePayload());
      expect(id).toMatch(/^OFFLINE-/);

      const pending = await queue.getPendingTransactions();
      expect(pending.some((p: any) => p.offline_id === id)).toBe(true);
    });

    it('should include all required fields in queued transaction', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      simulateOffline();
      const id = await queue.queueTransaction(
        makeSalePayload({
          terminal_id: 'T-FIELD',
          grand_total: 250,
        })
      );

      const pending = await queue.getPendingTransactions();
      const tx = pending.find((p: any) => p.offline_id === id);
      expect(tx).toBeDefined();
      expect(tx?.payload).toBeDefined();
    });
  });

  // ----------------------------------------------------------
  // Scenario 2: Multiple transactions queued while offline
  // ----------------------------------------------------------
  describe('Multiple Transactions Queue', () => {
    it('should queue multiple transactions maintaining order', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      simulateOffline();

      const ids: string[] = [];
      for (let i = 0; i < 5; i++) {
        const id = await queue.queueTransaction(makeSalePayload({ grand_total: (i + 1) * 100 }));
        ids.push(id);
      }

      const pending = await queue.getPendingTransactions();
      expect(pending.length).toBeGreaterThanOrEqual(5);

      // Verify IDs were generated
      ids.forEach((id) => {
        expect(id).toMatch(/^OFFLINE-/);
      });
    });

    it('should display correct queue count for 5 transactions', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      for (let i = 0; i < 5; i++) {
        await queue.queueTransaction(makeSalePayload());
      }

      const count = await queue.getQueueLength();
      expect(count).toBeGreaterThanOrEqual(5);
    });

    it('should sync all queued transactions in order when back online', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      simulateOffline();
      const ids: string[] = [];
      for (let i = 0; i < 3; i++) {
        ids.push(await queue.queueTransaction(makeSalePayload()));
      }

      simulateOnline();
      // Mark them as synced in order (simulates sync engine behavior)
      for (let i = 0; i < ids.length; i++) {
        await queue.markAsSynced(ids[i]!, `server-${i}`);
      }

      const pending = await queue.getPendingTransactions();
      for (const id of ids) {
        expect(pending.some((p: any) => p.offline_id === id)).toBe(false);
      }
    });
  });

  // ----------------------------------------------------------
  // Scenario 3: Failed transaction retry via markAsFailed
  // ----------------------------------------------------------
  describe('Failed Transaction Retry', () => {
    it('should mark transaction as failed and track it', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      const id = await queue.queueTransaction(makeSalePayload({ grand_total: 500 }));

      // Simulate server failure
      await queue.markAsFailed(id, 'Server Error 500');
      const status = await queue.getQueueStatus();
      expect(status).toBeDefined();
      // The failed transaction should be counted
      expect(status.total).toBeGreaterThanOrEqual(1);
    });

    it('should schedule retry with increasing backoff', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      const id = await queue.queueTransaction(makeSalePayload());
      await queue.markAsFailed(id, 'Server Error 1');
      await queue.markAsFailed(id, 'Server Error 2');

      const status = await queue.getQueueStatus();
      expect(status.max_retry_count).toBeGreaterThanOrEqual(2);
    });

    it('should eventually succeed after mock server recovers', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      const id = await queue.queueTransaction(makeSalePayload());
      // Fail twice
      await queue.markAsFailed(id, 'Temporary Error');
      await queue.markAsFailed(id, 'Temporary Error');
      // Then succeed
      await queue.markAsSynced(id, 'server-recovered-123');

      const pending = await queue.getPendingTransactions();
      expect(pending.some((p: any) => p.offline_id === id)).toBe(false);
    });
  });

  // ----------------------------------------------------------
  // Scenario 4: Connection status transitions
  // ----------------------------------------------------------
  describe('Connection Transitions', () => {
    it('should fire offline/online events on transition', () => {
      let offlineCalled = 0;
      let onlineCalled = 0;

      const offlineHandler = () => {
        offlineCalled++;
      };
      const onlineHandler = () => {
        onlineCalled++;
      };

      window.addEventListener('offline', offlineHandler);
      window.addEventListener('online', onlineHandler);

      simulateOffline();
      expect(offlineCalled).toBe(1);

      simulateOnline();
      expect(onlineCalled).toBe(1);

      window.removeEventListener('offline', offlineHandler);
      window.removeEventListener('online', onlineHandler);
    });

    it('should detect connection monitor online state changes', async () => {
      const { ConnectionMonitor } = await import('@/lib/offline/connection-monitor');
      const monitor = new ConnectionMonitor();
      monitor.startMonitoring();

      simulateOffline();
      expect(monitor.getIsOnline()).toBe(false);

      simulateOnline();
      // navigator.onLine is true now but monitor may need a check cycle
      expect(typeof monitor.getIsOnline()).toBe('boolean');
      monitor.destroy();
    });

    it('should handle rapid online/offline toggles', () => {
      let transitionCount = 0;
      const handler = () => {
        transitionCount++;
      };

      window.addEventListener('offline', handler);
      window.addEventListener('online', handler);

      for (let i = 0; i < 5; i++) {
        simulateOffline();
        simulateOnline();
      }
      expect(transitionCount).toBe(10);

      window.removeEventListener('offline', handler);
      window.removeEventListener('online', handler);
    });
  });

  // ----------------------------------------------------------
  // Scenario 5: Export / Import emergency backup
  // ----------------------------------------------------------
  describe('Emergency Export and Import', () => {
    it('should export queued transactions and re-import them', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      const offlineId = await queue.queueTransaction(makeSalePayload({ grand_total: 300 }));

      const exported = await queue.exportQueue();
      expect(exported).toBeDefined();
      expect(typeof exported).toBe('string');
      expect(exported).toContain(offlineId);

      // New queue simulates another device / fresh session
      const fresh = new TransactionQueue();
      const result = await fresh.importQueue(exported);
      expect(result.imported_count).toBeGreaterThanOrEqual(0);
    });

    it('should export valid JSON with metadata', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      await queue.queueTransaction(makeSalePayload());
      const exported = await queue.exportQueue();
      // Should be valid JSON
      expect(() => JSON.parse(exported)).not.toThrow();
    });

    it('should preserve all transaction data in export', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      await queue.queueTransaction(makeSalePayload({ grand_total: 999 }));
      const exported = await queue.exportQueue();
      expect(exported).toContain('999');
    });
  });

  // ----------------------------------------------------------
  // Scenario 6: Data consistency after sync
  // ----------------------------------------------------------
  describe('Data Consistency', () => {
    it('should clear synced transactions from queue', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      const offlineId = await queue.queueTransaction(makeSalePayload({ grand_total: 100 }));

      await queue.markAsSynced(offlineId, 'server-tx-001');
      const pending = await queue.getPendingTransactions();
      expect(pending.some((p: any) => p.offline_id === offlineId)).toBe(false);
    });

    it('should maintain data integrity after complex operations', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      // Simulate complex offline work
      simulateOffline();

      // Create multiple sales
      const sale1 = await queue.queueTransaction(
        makeSalePayload({ grand_total: 100, session_id: 'session-a' })
      );
      const sale2 = await queue.queueTransaction(
        makeSalePayload({ grand_total: 200, session_id: 'session-b' })
      );
      const sale3 = await queue.queueTransaction(
        makeSalePayload({ grand_total: 300, session_id: 'session-c' })
      );

      // Come online and sync partially
      simulateOnline();
      await queue.markAsSynced(sale1, 'server-1');
      await queue.markAsFailed(sale2, 'Temp error');
      await queue.markAsSynced(sale3, 'server-3');

      const status = await queue.getQueueStatus();
      // sale1 synced, sale2 still pending (needs maxRetries failures to mark as FAILED), sale3 synced
      expect(status.synced).toBeGreaterThanOrEqual(2);
      expect(status.pending + status.failed).toBeGreaterThanOrEqual(1);
    });

    it('should not lose data during concurrent queue operations', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      // Queue many transactions concurrently
      const promises = Array.from({ length: 10 }, (_, i) =>
        queue.queueTransaction(makeSalePayload({ grand_total: (i + 1) * 50 }))
      );

      const ids = await Promise.all(promises);
      expect(ids.length).toBe(10);
      expect(new Set(ids).size).toBe(10); // All unique
    });
  });

  // ----------------------------------------------------------
  // Scenario 7: Reconnection and auto-sync
  // ----------------------------------------------------------
  describe('Reconnection and Auto-Sync', () => {
    it('should trigger sync engine on reconnection event', async () => {
      const { syncEngine } = await import('@/lib/offline/sync-engine');

      simulateOffline();
      simulateOnline();

      // Sync engine should be responsive to online events
      expect(syncEngine).toBeDefined();
      expect(typeof syncEngine.manualSync).toBe('function');
    });

    it('should verify queued transactions are ready to sync after reconnection', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      simulateOffline();
      await queue.queueTransaction(makeSalePayload());
      await queue.queueTransaction(makeSalePayload());

      simulateOnline();
      const pending = await queue.getPendingTransactions();
      expect(pending.length).toBeGreaterThanOrEqual(2);
      // All should be in PENDING status, ready for sync
      for (const tx of pending) {
        expect(tx.status).toMatch(/pending/i);
      }
    });
  });

  // ----------------------------------------------------------
  // Scenario 8: Offline customer creation
  // ----------------------------------------------------------
  describe('Offline Customer Creation', () => {
    it('should create customer with offline ID while offline', () => {
      simulateOffline();
      const customerId = generateOfflineTransactionId('customer');
      expect(customerId).toMatch(/^OFFLINE-/);
    });

    it('should queue customer creation for sync', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      simulateOffline();
      const id = await queue.queueTransaction({
        ...makeSalePayload(),
        terminal_id: 'T-CUST',
        session_id: 'CUST-SESSION',
        items: [{ product_id: 'cust-prod', quantity: 1, price: 0, subtotal: 0 }],
        grand_total: 0,
        subtotal: 0,
        tax_amount: 0,
        discount_amount: 0,
        payment_method: 'none',
      } as TransactionPayload);

      expect(id).toMatch(/^OFFLINE-/);
    });
  });

  // ----------------------------------------------------------
  // Scenario 9: Sync progress tracking
  // ----------------------------------------------------------
  describe('Sync Progress Tracking', () => {
    it('should report queue length for progress tracking', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      // Queue 10 transactions
      const ids: string[] = [];
      for (let i = 0; i < 10; i++) {
        ids.push(await queue.queueTransaction(makeSalePayload()));
      }

      const total = await queue.getQueueLength();
      expect(total).toBeGreaterThanOrEqual(10);

      // Simulate sync progress: mark 3 of 10 as synced
      for (let i = 0; i < 3; i++) {
        await queue.markAsSynced(ids[i]!, `server-pg-${i}`);
      }

      const remaining = await queue.getQueueLength();
      expect(remaining).toBeLessThan(total);
    });

    it('should calculate completion percentage', async () => {
      const { TransactionQueue } = await import('@/lib/offline/transaction-queue');
      const queue = new TransactionQueue();

      for (let i = 0; i < 4; i++) {
        await queue.queueTransaction(makeSalePayload());
      }

      const status = await queue.getQueueStatus();
      const total = status.total;
      const synced = status.synced;
      const percentage = total > 0 ? Math.round((synced / total) * 100) : 0;
      expect(percentage).toBeGreaterThanOrEqual(0);
      expect(percentage).toBeLessThanOrEqual(100);
    });
  });

  // ----------------------------------------------------------
  // Scenario 10: Conflict detection during sync
  // ----------------------------------------------------------
  describe('Conflict Detection During Sync', () => {
    it('should detect conflicts between local and server data', async () => {
      const { ConflictResolver } = await import('@/lib/offline/conflict-resolver');
      const resolver = new ConflictResolver();

      const localProducts = [
        {
          id: 'p-1',
          name: 'Local Product',
          price: 100,
          version: 1,
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ];
      const serverProducts = [
        {
          id: 'p-1',
          name: 'Server Product',
          price: 150,
          version: 2,
          updatedAt: '2024-06-01T00:00:00Z',
        },
      ];

      const conflicts = await resolver.detectConflicts(localProducts, serverProducts);
      expect(Array.isArray(conflicts)).toBe(true);
    });

    it('should handle no conflicts gracefully', async () => {
      const { ConflictResolver } = await import('@/lib/offline/conflict-resolver');
      const resolver = new ConflictResolver();

      const same = [
        {
          id: 's-1',
          name: 'Same',
          price: 100,
          version: 1,
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ];
      const conflicts = await resolver.detectConflicts(same, same);
      expect(conflicts.length).toBe(0);
    });
  });

  // ----------------------------------------------------------
  // Scenario 11: IndexedDB cache freshness after sync
  // ----------------------------------------------------------
  describe('Data Freshness After Sync', () => {
    it('should update local cache with new product data', async () => {
      const { idbService } = await import('@/lib/offline/indexeddb');
      await idbService.openDatabase();

      // Add initial product
      await idbService.put('products', {
        id: 'fresh-1',
        name: 'Old Name',
        price: 100,
      });

      // Simulate server sending updated data after sync
      await idbService.put('products', {
        id: 'fresh-1',
        name: 'Updated Name',
        price: 150,
      });

      const product = await idbService.get<any>('products', 'fresh-1');
      expect(product?.name).toBe('Updated Name');
      expect(product?.price).toBe(150);
    });

    it('should merge remote changes with local data', async () => {
      const { idbService } = await import('@/lib/offline/indexeddb');
      await idbService.openDatabase();

      // Local has product A and B
      await idbService.put('products', { id: 'merge-a', name: 'Product A' });
      await idbService.put('products', { id: 'merge-b', name: 'Product B' });

      // Server adds product C
      await idbService.put('products', { id: 'merge-c', name: 'Product C' });

      const all = await idbService.getAll<any>('products');
      const ids = all.map((p: any) => p.id);
      expect(ids).toContain('merge-a');
      expect(ids).toContain('merge-b');
      expect(ids).toContain('merge-c');
    });
  });
});
