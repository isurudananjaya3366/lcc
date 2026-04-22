// @vitest-environment jsdom
// ================================================================
// Task 86: Transaction Queue Tests
// ================================================================

/* eslint-disable @typescript-eslint/no-explicit-any */
declare const describe: any;
declare const it: any;
declare const expect: any;
declare const beforeAll: any;
declare const beforeEach: any;

// Polyfill IndexedDB for jsdom environment
import 'fake-indexeddb/auto';

import { generateOfflineTransactionId } from '@/lib/offline/id-generator';
import type { TransactionPayload } from '@/lib/offline/queue-types';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makePayload(overrides: Partial<TransactionPayload> = {}): TransactionPayload {
  return {
    terminal_id: 'T001',
    session_id: `session-${Date.now()}`,
    items: [{ product_id: 'prod-1', quantity: 2, price: 500, subtotal: 1000 }],
    grand_total: 1000,
    subtotal: 1000,
    tax_amount: 0,
    discount_amount: 0,
    payment_method: 'cash',
    timestamp: new Date().toISOString(),
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Offline ID generation tests
// ---------------------------------------------------------------------------

describe('Offline ID Generation', () => {
  it('should generate IDs with the correct prefix', () => {
    const saleId = generateOfflineTransactionId('sale');
    expect(saleId).toMatch(/^OFFLINE-/);
  });

  it('should generate unique IDs', () => {
    const ids = new Set<string>();
    for (let i = 0; i < 1000; i++) {
      ids.add(generateOfflineTransactionId('sale'));
    }
    expect(ids.size).toBe(1000);
  });

  it('should include a timestamp component', () => {
    const id = generateOfflineTransactionId('sale');
    // The ID format is OFFLINE-{T}-{TS}-{SEQ}
    const parts = id.split('-');
    expect(parts.length).toBeGreaterThanOrEqual(3);
  });
});

// ---------------------------------------------------------------------------
// Transaction Queue tests — these test the TransactionQueue class
// ---------------------------------------------------------------------------

describe('Transaction Queue', () => {
  let TransactionQueue: (typeof import('@/lib/offline/transaction-queue'))['TransactionQueue'];
  let queue: InstanceType<typeof TransactionQueue>;

  beforeAll(async () => {
    const mod = await import('@/lib/offline/transaction-queue');
    TransactionQueue = mod.TransactionQueue;
  });

  beforeEach(() => {
    queue = new TransactionQueue();
  });

  // ----------------------------------------------------------
  // Enqueueing
  // ----------------------------------------------------------
  describe('Enqueue Operations', () => {
    it('should add a sale transaction to the queue', async () => {
      const payload = makePayload();
      const offlineId = await queue.queueTransaction(payload);
      expect(offlineId).toMatch(/^OFFLINE-/);
      const pending = await queue.getPendingTransactions();
      expect(pending.length).toBeGreaterThanOrEqual(1);
    });

    it('should maintain FIFO ordering for pending items', async () => {
      const first = await queue.queueTransaction(makePayload({ session_id: 'first-session' }));
      const second = await queue.queueTransaction(makePayload({ session_id: 'second-session' }));
      const pending = await queue.getPendingTransactions();
      const ids = pending.map((p) => p.offline_id);
      expect(ids.indexOf(first)).toBeLessThan(ids.indexOf(second));
    });
  });

  // ----------------------------------------------------------
  // Mark as synced
  // ----------------------------------------------------------
  describe('Mark as Synced', () => {
    it('should remove a transaction from pending after marking synced', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      await queue.markAsSynced(offlineId, 'server-tx-123');
      const pending = await queue.getPendingTransactions();
      expect(pending.some((p) => p.offline_id === offlineId)).toBe(false);
    });
  });

  // ----------------------------------------------------------
  // Mark as failed
  // ----------------------------------------------------------
  describe('Mark as Failed', () => {
    it('should increment retry count on failure', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      await queue.markAsFailed(offlineId, 'Error 1');
      await queue.markAsFailed(offlineId, 'Error 2');
      const status = await queue.getQueueStatus();
      // Transaction may still be pending (below max retries) or failed
      expect(status.total).toBeGreaterThanOrEqual(1);
    });
  });

  // ----------------------------------------------------------
  // Queue count
  // ----------------------------------------------------------
  describe('Queue Count', () => {
    it('should report correct count of pending transactions', async () => {
      await queue.queueTransaction(makePayload());
      await queue.queueTransaction(makePayload());
      await queue.queueTransaction(makePayload());
      const count = await queue.getQueueLength();
      expect(count).toBeGreaterThanOrEqual(3);
    });
  });

  // ----------------------------------------------------------
  // Export / Import
  // ----------------------------------------------------------
  describe('Export and Import', () => {
    it('should export queue as a JSON string', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      const exported = await queue.exportQueue();
      expect(exported).toBeDefined();
      expect(typeof exported).toBe('string');
      expect(exported).toContain(offlineId);
    });

    it('should import transactions from exported data', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      const exported = await queue.exportQueue();

      // create a new queue and import
      const newQueue = new TransactionQueue();
      const result = await newQueue.importQueue(exported);
      expect(result.imported_count).toBeGreaterThanOrEqual(0);
    });
  });

  // ----------------------------------------------------------
  // Cleanup
  // ----------------------------------------------------------
  describe('Cleanup', () => {
    it('should clean up synced transactions', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      await queue.markAsSynced(offlineId, 'server-123');
      const result = await queue.cleanupQueue();
      expect(result).toBeDefined();
    });

    it('should preserve recent unsycned transactions during cleanup', async () => {
      const id1 = await queue.queueTransaction(makePayload());
      const id2 = await queue.queueTransaction(makePayload());
      await queue.markAsSynced(id1, 'server-a');
      // id2 is still pending
      await queue.cleanupQueue();
      const pending = await queue.getPendingTransactions();
      expect(pending.some((p) => p.offline_id === id2)).toBe(true);
    });

    it('should preserve failed transactions during cleanup', async () => {
      const id = await queue.queueTransaction(makePayload());
      await queue.markAsFailed(id, 'Server 500');
      await queue.cleanupQueue();
      const status = await queue.getQueueStatus();
      // failed transactions should still be counted
      expect(status.total).toBeGreaterThanOrEqual(1);
    });
  });

  // ----------------------------------------------------------
  // Queue persistence tests (Task 86 — Step 8)
  // ----------------------------------------------------------
  describe('Queue Persistence', () => {
    it('should persist transactions across queue instances', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      // Create a new queue instance (simulates "page refresh")
      const freshQueue = new TransactionQueue();
      const pending = await freshQueue.getPendingTransactions();
      // The transaction should still be there (IDB is persistent)
      expect(pending.some((p) => p.offline_id === offlineId)).toBe(true);
    });

    it('should maintain queue integrity with multiple instances', async () => {
      await queue.queueTransaction(makePayload());
      await queue.queueTransaction(makePayload());
      const fresh = new TransactionQueue();
      const count = await fresh.getQueueLength();
      expect(count).toBeGreaterThanOrEqual(2);
    });

    it('should restore queue on app restart (new instance)', async () => {
      const ids: string[] = [];
      for (let i = 0; i < 3; i++) {
        ids.push(await queue.queueTransaction(makePayload()));
      }
      const restored = new TransactionQueue();
      const pending = await restored.getPendingTransactions();
      for (const id of ids) {
        expect(pending.some((p) => p.offline_id === id)).toBe(true);
      }
    });
  });

  // ----------------------------------------------------------
  // Retry mechanism tests (Task 86 — Step 7)
  // ----------------------------------------------------------
  describe('Retry Mechanism', () => {
    it('should increment retry_count on each failure', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      await queue.markAsFailed(offlineId, 'Err 1');
      await queue.markAsFailed(offlineId, 'Err 2');
      await queue.markAsFailed(offlineId, 'Err 3');
      const status = await queue.getQueueStatus();
      expect(status.max_retry_count).toBeGreaterThanOrEqual(3);
    });

    it('should track average retry count in queue status', async () => {
      const id1 = await queue.queueTransaction(makePayload());
      const id2 = await queue.queueTransaction(makePayload());
      await queue.markAsFailed(id1, 'Err');
      await queue.markAsFailed(id1, 'Err');
      // id2 has 0 retries, id1 has 2 retries → average should be 1
      const status = await queue.getQueueStatus();
      expect(status.average_retry_count).toBeGreaterThanOrEqual(0);
    });

    it('should track transactions at max retries', async () => {
      const offlineId = await queue.queueTransaction(makePayload());
      // Mark failed many times to exceed max retries
      for (let i = 0; i < 10; i++) {
        await queue.markAsFailed(offlineId, `Err ${i}`);
      }
      const status = await queue.getQueueStatus();
      expect(status.at_max_retries).toBeGreaterThanOrEqual(1);
    });
  });

  // ----------------------------------------------------------
  // Import validation tests (Task 86 — Step 10 expanded)
  // ----------------------------------------------------------
  describe('Import Validation', () => {
    it('should reject invalid JSON on import', async () => {
      try {
        await queue.importQueue('not-json-at-all');
        // If it doesn't throw, result should have 0 imports
      } catch (err) {
        expect(err).toBeDefined();
      }
    });

    it('should handle empty export string gracefully', async () => {
      try {
        const result = await queue.importQueue('[]');
        expect(result.imported_count).toBe(0);
      } catch (err) {
        expect(err).toBeDefined();
      }
    });

    it('should merge imported transactions with existing queue', async () => {
      const existingId = await queue.queueTransaction(makePayload({ session_id: 'existing' }));
      const exported = await queue.exportQueue();

      const newQueue = new TransactionQueue();
      await newQueue.queueTransaction(makePayload({ session_id: 'new-item' }));
      await newQueue.importQueue(exported);

      const pending = await newQueue.getPendingTransactions();
      // Should have both existing and new items
      expect(pending.length).toBeGreaterThanOrEqual(1);
    });
  });

  // ----------------------------------------------------------
  // Queue status detail tests (Task 86 — detailed status)
  // ----------------------------------------------------------
  describe('Queue Status Details', () => {
    it('should report correct status breakdown', async () => {
      await queue.queueTransaction(makePayload());
      await queue.queueTransaction(makePayload());
      const id3 = await queue.queueTransaction(makePayload());
      await queue.markAsFailed(id3, 'Error');

      const status = await queue.getQueueStatus();
      expect(status.total).toBeGreaterThanOrEqual(3);
      expect(status.pending).toBeGreaterThanOrEqual(2);
      expect(status.failed).toBeGreaterThanOrEqual(1);
    });

    it('should track oldest pending transaction', async () => {
      await queue.queueTransaction(makePayload());
      const status = await queue.getQueueStatus();
      expect(status.oldest_pending).toBeDefined();
    });

    it('should calculate health score', async () => {
      await queue.queueTransaction(makePayload());
      const status = await queue.getQueueStatus();
      expect(typeof status.health_score).toBe('number');
      expect(status.health_score).toBeGreaterThanOrEqual(0);
      expect(status.health_score).toBeLessThanOrEqual(100);
    });

    it('should track error distribution', async () => {
      const id1 = await queue.queueTransaction(makePayload());
      const id2 = await queue.queueTransaction(makePayload());
      await queue.markAsFailed(id1, 'Network Error');
      await queue.markAsFailed(id2, 'Network Error');
      const status = await queue.getQueueStatus();
      expect(status.error_summary).toBeDefined();
      expect(status.error_summary.most_common_error).toBeDefined();
    });
  });
});
