// ================================================================
// IndexedDB Mock Utilities — Task 85
// ================================================================
// Provides in-memory mock implementations of the IDB service
// for test environments where fake-indexeddb is not available.
// ================================================================

/* eslint-disable @typescript-eslint/no-explicit-any */

type StoreData = Map<string, any>;

class MockIDBService {
  private stores: Map<string, StoreData> = new Map();
  private opened = false;

  async openDatabase(): Promise<void> {
    if (!this.opened) {
      this.stores.set('products', new Map());
      this.stores.set('customers', new Map());
      this.stores.set('transactions', new Map());
      this.stores.set('settings', new Map());
      this.stores.set('sync_meta', new Map());
      this.stores.set('categories', new Map());
      this.opened = true;
    }
  }

  async put(storeName: string, data: any): Promise<void> {
    const store = this.getStore(storeName);
    const key = data.id ?? data.key;
    if (!key) throw new Error('Record must have an id or key');
    store.set(key, structuredClone(data));
  }

  async get<T = any>(storeName: string, key: string): Promise<T | undefined> {
    const store = this.getStore(storeName);
    const value = store.get(key);
    return value ? (structuredClone(value) as T) : undefined;
  }

  async getAll<T = any>(storeName: string): Promise<T[]> {
    const store = this.getStore(storeName);
    return Array.from(store.values()).map((v) => structuredClone(v) as T);
  }

  async delete(storeName: string, key: string): Promise<void> {
    const store = this.getStore(storeName);
    store.delete(key);
  }

  async clear(storeName: string): Promise<void> {
    const store = this.getStore(storeName);
    store.clear();
  }

  async count(storeName: string): Promise<number> {
    const store = this.getStore(storeName);
    return store.size;
  }

  async bulkPut(storeName: string, items: any[]): Promise<void> {
    for (const item of items) {
      await this.put(storeName, item);
    }
  }

  async bulkDelete(storeName: string, keys: string[]): Promise<void> {
    for (const key of keys) {
      await this.delete(storeName, key);
    }
  }

  async close(): Promise<void> {
    this.opened = false;
  }

  private getStore(name: string): StoreData {
    const store = this.stores.get(name);
    if (!store) throw new Error(`Object store "${name}" not found`);
    return store;
  }
}

export const mockIdbService = new MockIDBService();

/**
 * Reset all mock stores — call in beforeEach/afterEach.
 */
export function resetMockIDB(): void {
  mockIdbService.close();
}
