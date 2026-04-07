// ================================================================
// Transactions Object Store — Task 24
// ================================================================
// Offline transaction queue — create, query, update sync status.
// ================================================================

import { idbService } from '../indexeddb';
import { ObjectStoreNames, type Transaction } from '../schema';

const STORE = ObjectStoreNames.TRANSACTIONS;

class TransactionsService {
  async addTransaction(transaction: Transaction): Promise<void> {
    await idbService.put(STORE, transaction);
  }

  async getTransaction(offlineId: string): Promise<Transaction | undefined> {
    return idbService.get<Transaction>(STORE, offlineId);
  }

  async getAllTransactions(): Promise<Transaction[]> {
    return idbService.getAll<Transaction>(STORE);
  }

  async getPendingTransactions(): Promise<Transaction[]> {
    return idbService.getAllByIndex<Transaction>(
      STORE,
      'sync_status',
      'pending'
    );
  }

  async getFailedTransactions(): Promise<Transaction[]> {
    return idbService.getAllByIndex<Transaction>(
      STORE,
      'sync_status',
      'failed'
    );
  }

  async updateTransactionSyncStatus(
    offlineId: string,
    newStatus: Transaction['sync_status']
  ): Promise<void> {
    const tx = await this.getTransaction(offlineId);
    if (!tx) throw new Error(`Transaction ${offlineId} not found`);
    tx.sync_status = newStatus;
    tx.last_sync_attempt = new Date().toISOString();
    await idbService.put(STORE, tx);
  }

  async markTransactionSynced(
    offlineId: string,
    serverId: string
  ): Promise<void> {
    const tx = await this.getTransaction(offlineId);
    if (!tx) throw new Error(`Transaction ${offlineId} not found`);
    tx.sync_status = 'synced';
    tx.server_id = serverId;
    tx.synced_at = new Date().toISOString();
    await idbService.put(STORE, tx);
  }

  async markTransactionFailed(offlineId: string, error: string): Promise<void> {
    const tx = await this.getTransaction(offlineId);
    if (!tx) throw new Error(`Transaction ${offlineId} not found`);
    tx.sync_status = 'failed';
    tx.sync_error = error;
    tx.sync_attempts += 1;
    tx.last_sync_attempt = new Date().toISOString();
    await idbService.put(STORE, tx);
  }

  async retryFailedTransactions(): Promise<Transaction[]> {
    const failed = await this.getFailedTransactions();
    for (const tx of failed) {
      tx.sync_status = 'pending';
      tx.sync_error = undefined;
      await idbService.put(STORE, tx);
    }
    return failed;
  }

  async deleteOldTransactions(ageDays: number): Promise<number> {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - ageDays);
    const cutoffISO = cutoff.toISOString();

    const all = await this.getAllTransactions();
    const toDelete = all.filter(
      (tx) => tx.sync_status === 'synced' && tx.created_at < cutoffISO
    );

    if (toDelete.length > 0) {
      await idbService.bulkDelete(
        STORE,
        toDelete.map((tx) => tx.offline_id)
      );
    }

    return toDelete.length;
  }

  async getTransactionStats(): Promise<TransactionStats> {
    const all = await this.getAllTransactions();
    return {
      total: all.length,
      pending: all.filter((t) => t.sync_status === 'pending').length,
      syncing: all.filter((t) => t.sync_status === 'syncing').length,
      synced: all.filter((t) => t.sync_status === 'synced').length,
      failed: all.filter((t) => t.sync_status === 'failed').length,
    };
  }

  async getTransactionCount(): Promise<number> {
    return idbService.count(STORE);
  }
}

export interface TransactionStats {
  total: number;
  pending: number;
  syncing: number;
  synced: number;
  failed: number;
}

export const transactionsService = new TransactionsService();
