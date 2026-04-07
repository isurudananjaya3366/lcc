// ================================================================
// IndexedDB Service — Task 17
// ================================================================
// Low-level wrapper around the browser IndexedDB API providing
// typed, Promise-based access to object stores.
// ================================================================

import {
  DATABASE_NAME,
  DATABASE_VERSION,
  upgradeDatabaseSchema,
} from './schema';

// ── Types ──────────────────────────────────────────────────────

export type ConnectionState = 'closed' | 'connecting' | 'open' | 'error';

export interface IDBErrorInfo {
  name: string;
  message: string;
  storeName?: string;
  operation?: string;
}

// ── Service ────────────────────────────────────────────────────

class IDBService {
  private db: IDBDatabase | null = null;
  private state: ConnectionState = 'closed';
  private openPromise: Promise<IDBDatabase> | null = null;

  /** Open (or reuse) the database connection. */
  async openDatabase(): Promise<IDBDatabase> {
    if (this.db && this.state === 'open') return this.db;
    if (this.openPromise) return this.openPromise;

    this.state = 'connecting';

    this.openPromise = new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        const oldVersion = event.oldVersion;
        upgradeDatabaseSchema(db, oldVersion);
      };

      request.onsuccess = (event) => {
        this.db = (event.target as IDBOpenDBRequest).result;
        this.state = 'open';
        this.openPromise = null;

        this.db.onclose = () => {
          this.state = 'closed';
          this.db = null;
        };

        resolve(this.db);
      };

      request.onerror = () => {
        this.state = 'error';
        this.openPromise = null;
        reject(this.wrapError(request.error, 'openDatabase'));
      };
    });

    return this.openPromise;
  }

  /** Start a transaction on the given stores. */
  startTransaction(
    stores: string | string[],
    mode: IDBTransactionMode = 'readonly'
  ): IDBTransaction {
    if (!this.db) throw new Error('Database not open');
    return this.db.transaction(stores, mode);
  }

  // ── Single-record operations ─────────────────────────────────

  async get<T = unknown>(
    storeName: string,
    key: IDBValidKey
  ): Promise<T | undefined> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const req = tx.objectStore(storeName).get(key);
      req.onsuccess = () => resolve(req.result as T | undefined);
      req.onerror = () => reject(this.wrapError(req.error, 'get', storeName));
    });
  }

  async getAll<T = unknown>(storeName: string): Promise<T[]> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const req = tx.objectStore(storeName).getAll();
      req.onsuccess = () => resolve(req.result as T[]);
      req.onerror = () =>
        reject(this.wrapError(req.error, 'getAll', storeName));
    });
  }

  async put(storeName: string, value: unknown): Promise<IDBValidKey> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const req = tx.objectStore(storeName).put(value);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(this.wrapError(req.error, 'put', storeName));
    });
  }

  async add(storeName: string, value: unknown): Promise<IDBValidKey> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const req = tx.objectStore(storeName).add(value);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(this.wrapError(req.error, 'add', storeName));
    });
  }

  async delete(storeName: string, key: IDBValidKey): Promise<void> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const req = tx.objectStore(storeName).delete(key);
      req.onsuccess = () => resolve();
      req.onerror = () =>
        reject(this.wrapError(req.error, 'delete', storeName));
    });
  }

  async clear(storeName: string): Promise<void> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const req = tx.objectStore(storeName).clear();
      req.onsuccess = () => resolve();
      req.onerror = () => reject(this.wrapError(req.error, 'clear', storeName));
    });
  }

  // ── Index-based queries ──────────────────────────────────────

  async getByIndex<T = unknown>(
    storeName: string,
    indexName: string,
    value: IDBValidKey
  ): Promise<T | undefined> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const idx = tx.objectStore(storeName).index(indexName);
      const req = idx.get(value);
      req.onsuccess = () => resolve(req.result as T | undefined);
      req.onerror = () =>
        reject(this.wrapError(req.error, 'getByIndex', storeName));
    });
  }

  async getAllByIndex<T = unknown>(
    storeName: string,
    indexName: string,
    value: IDBValidKey
  ): Promise<T[]> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const idx = tx.objectStore(storeName).index(indexName);
      const req = idx.getAll(value);
      req.onsuccess = () => resolve(req.result as T[]);
      req.onerror = () =>
        reject(this.wrapError(req.error, 'getAllByIndex', storeName));
    });
  }

  // ── Cursor ───────────────────────────────────────────────────

  async openCursor<T = unknown>(
    storeName: string,
    direction: IDBCursorDirection = 'next',
    callback: (value: T, cursor: IDBCursorWithValue) => void
  ): Promise<void> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const req = tx.objectStore(storeName).openCursor(null, direction);
      req.onsuccess = () => {
        const cursor = req.result;
        if (cursor) {
          callback(cursor.value as T, cursor);
          cursor.continue();
        } else {
          resolve();
        }
      };
      req.onerror = () =>
        reject(this.wrapError(req.error, 'openCursor', storeName));
    });
  }

  // ── Bulk operations ──────────────────────────────────────────

  async bulkPut(storeName: string, values: unknown[]): Promise<number> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      let count = 0;

      for (const value of values) {
        const req = store.put(value);
        req.onsuccess = () => {
          count++;
        };
      }

      tx.oncomplete = () => resolve(count);
      tx.onerror = () => reject(this.wrapError(tx.error, 'bulkPut', storeName));
    });
  }

  async bulkDelete(storeName: string, keys: IDBValidKey[]): Promise<number> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      let count = 0;

      for (const key of keys) {
        const req = store.delete(key);
        req.onsuccess = () => {
          count++;
        };
      }

      tx.oncomplete = () => resolve(count);
      tx.onerror = () =>
        reject(this.wrapError(tx.error, 'bulkDelete', storeName));
    });
  }

  // ── Utilities ────────────────────────────────────────────────

  async count(storeName: string): Promise<number> {
    const db = await this.openDatabase();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const req = tx.objectStore(storeName).count();
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(this.wrapError(req.error, 'count', storeName));
    });
  }

  getConnectionState(): ConnectionState {
    return this.state;
  }

  async close(): Promise<void> {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.state = 'closed';
    }
  }

  // ── Error helper ─────────────────────────────────────────────

  private wrapError(
    error: DOMException | null,
    operation: string,
    storeName?: string
  ): IDBErrorInfo {
    return {
      name: error?.name ?? 'UnknownError',
      message: error?.message ?? 'An unknown IndexedDB error occurred',
      storeName,
      operation,
    };
  }
}

// Singleton export
export const idbService = new IDBService();
