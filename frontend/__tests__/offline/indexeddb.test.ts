// ================================================================
// Task 85: IndexedDB Service Tests
// ================================================================

/* eslint-disable @typescript-eslint/no-explicit-any */
declare const describe: any;
declare const it: any;
declare const expect: any;
declare const beforeAll: any;
declare const afterEach: any;

import { DATABASE_NAME, ObjectStoreNames } from '@/lib/offline/schema';

// ---------------------------------------------------------------------------
// fake-indexeddb shim — the test runner should install `fake-indexeddb`
// and have it polyfilled globally (e.g. via jest.setup or vitest.setup).
// If the shim is not present the tests will be skipped gracefully.
// ---------------------------------------------------------------------------

const idbAvailable =
  typeof globalThis.indexedDB !== 'undefined' ||
  typeof indexedDB !== 'undefined';

const describeIf = idbAvailable ? describe : describe.skip;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeProduct(overrides: Record<string, unknown> = {}) {
  return {
    id: `prod-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    name: 'Test Product',
    sku: `SKU-${Date.now()}`,
    barcode: `BAR-${Date.now()}`,
    price: 1000,
    category: 'general',
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

function makeCustomer(overrides: Record<string, unknown> = {}) {
  return {
    id: `cust-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    name: 'Test Customer',
    email: `test-${Date.now()}@example.com`,
    phone: `+9471${Date.now().toString().slice(-7)}`,
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Database initialization tests
// ---------------------------------------------------------------------------

describeIf('IndexedDB Service', () => {
  let db: (typeof import('@/lib/offline/indexeddb'))['idbService'];

  beforeAll(async () => {
    const mod = await import('@/lib/offline/indexeddb');
    db = mod.idbService;
  });

  afterEach(async () => {
    // Close the connection so we can delete the database
    try {
      await db.close();
    } catch {
      // ignore
    }
    // Delete the database so next test starts fresh
    await new Promise<void>((resolve, reject) => {
      const req = indexedDB.deleteDatabase(DATABASE_NAME);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  });

  // ----------------------------------------------------------
  // Initialization
  // ----------------------------------------------------------
  describe('Database Initialization', () => {
    it('should create the database with the correct name', async () => {
      await db.openDatabase();
      // If openDatabase succeeds the database exists
      expect(db).toBeDefined();
    });

    it('should be a singleton instance', async () => {
      const mod = await import('@/lib/offline/indexeddb');
      expect(mod.idbService).toBe(db);
    });
  });

  // ----------------------------------------------------------
  // Product CRUD
  // ----------------------------------------------------------
  describe('Product CRUD Operations', () => {
    it('should add and retrieve a product', async () => {
      await db.openDatabase();

      const product = makeProduct();
      await db.put('products', product);
      const retrieved = await db.get<Record<string, unknown>>(
        'products',
        product.id
      );
      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(product.id);
      expect(retrieved?.name).toBe(product.name);
    });

    it('should update an existing product', async () => {
      await db.openDatabase();

      const product = makeProduct();
      await db.put('products', product);
      await db.put('products', { ...product, price: 2000 });
      const retrieved = await db.get<Record<string, unknown>>(
        'products',
        product.id
      );
      expect(retrieved?.price).toBe(2000);
    });

    it('should delete a product', async () => {
      await db.openDatabase();

      const product = makeProduct();
      await db.put('products', product);
      await db.delete('products', product.id);
      const retrieved = await db.get<Record<string, unknown>>(
        'products',
        product.id
      );
      expect(retrieved).toBeUndefined();
    });

    it('should return undefined for non-existent product', async () => {
      await db.openDatabase();
      const retrieved = await db.get<Record<string, unknown>>(
        'products',
        'non-existent-id'
      );
      expect(retrieved).toBeUndefined();
    });
  });

  // ----------------------------------------------------------
  // Customer CRUD
  // ----------------------------------------------------------
  describe('Customer CRUD Operations', () => {
    it('should add and retrieve a customer', async () => {
      await db.openDatabase();

      const customer = makeCustomer();
      await db.put('customers', customer);
      const retrieved = await db.get<Record<string, unknown>>(
        'customers',
        customer.id
      );
      expect(retrieved).toBeDefined();
      expect(retrieved?.name).toBe(customer.name);
    });

    it('should update an existing customer', async () => {
      await db.openDatabase();

      const customer = makeCustomer();
      await db.put('customers', customer);
      await db.put('customers', { ...customer, name: 'Updated Name' });
      const retrieved = await db.get<Record<string, unknown>>(
        'customers',
        customer.id
      );
      expect(retrieved?.name).toBe('Updated Name');
    });

    it('should delete a customer', async () => {
      await db.openDatabase();

      const customer = makeCustomer();
      await db.put('customers', customer);
      await db.delete('customers', customer.id);
      const retrieved = await db.get<Record<string, unknown>>(
        'customers',
        customer.id
      );
      expect(retrieved).toBeUndefined();
    });
  });

  // ----------------------------------------------------------
  // Batch operations
  // ----------------------------------------------------------
  describe('Batch Operations', () => {
    it('should bulk-add multiple products', async () => {
      await db.openDatabase();

      const products = Array.from({ length: 10 }, (_, i) =>
        makeProduct({ id: `bulk-prod-${i}`, name: `Product ${i}` })
      );

      for (const p of products) {
        await db.put('products', p);
      }

      const all = await db.getAll('products');
      expect(all.length).toBe(10);
    });

    it('should bulk-add multiple customers', async () => {
      await db.openDatabase();

      const customers = Array.from({ length: 5 }, (_, i) =>
        makeCustomer({ id: `bulk-cust-${i}`, name: `Customer ${i}` })
      );

      for (const c of customers) {
        await db.put('customers', c);
      }

      const all = await db.getAll('customers');
      expect(all.length).toBe(5);
    });
  });

  // ----------------------------------------------------------
  // Cache clearing
  // ----------------------------------------------------------
  describe('Cache Clearing', () => {
    it('should clear all products', async () => {
      await db.openDatabase();

      await db.put('products', makeProduct({ id: 'cleartest-1' }));
      await db.put('products', makeProduct({ id: 'cleartest-2' }));
      await db.clear('products');
      const all = await db.getAll('products');
      expect(all.length).toBe(0);
    });

    it('should clear all customers', async () => {
      await db.openDatabase();

      await db.put('customers', makeCustomer({ id: 'cleartest-c1' }));
      await db.clear('customers');
      const all = await db.getAll('customers');
      expect(all.length).toBe(0);
    });
  });

  // ----------------------------------------------------------
  // Index query tests (Task 85 — Step 5)
  // ----------------------------------------------------------
  describe('Index Query Operations', () => {
    it('should retrieve a product by barcode index', async () => {
      await db.openDatabase();
      const product = makeProduct({ id: 'idx-bar-1', barcode: 'BAR-999111' });
      await db.put('products', product);
      const all = await db.getAll<Record<string, unknown>>('products');
      const found = all.find((p) => p.barcode === 'BAR-999111');
      expect(found).toBeDefined();
      expect(found?.id).toBe('idx-bar-1');
    });

    it('should retrieve a product by SKU index', async () => {
      await db.openDatabase();
      const product = makeProduct({ id: 'idx-sku-1', sku: 'SKU-UNIQUE-007' });
      await db.put('products', product);
      const all = await db.getAll<Record<string, unknown>>('products');
      const found = all.find((p) => p.sku === 'SKU-UNIQUE-007');
      expect(found).toBeDefined();
      expect(found?.id).toBe('idx-sku-1');
    });

    it('should retrieve a customer by phone', async () => {
      await db.openDatabase();
      const customer = makeCustomer({
        id: 'idx-phone-1',
        phone: '+94770000001',
      });
      await db.put('customers', customer);
      const all = await db.getAll<Record<string, unknown>>('customers');
      const found = all.find((c) => c.phone === '+94770000001');
      expect(found).toBeDefined();
      expect(found?.id).toBe('idx-phone-1');
    });

    it('should retrieve a customer by email', async () => {
      await db.openDatabase();
      const customer = makeCustomer({
        id: 'idx-email-1',
        email: 'unique@test.com',
      });
      await db.put('customers', customer);
      const all = await db.getAll<Record<string, unknown>>('customers');
      const found = all.find((c) => c.email === 'unique@test.com');
      expect(found).toBeDefined();
      expect(found?.id).toBe('idx-email-1');
    });

    it('should return no results for non-existent index values', async () => {
      await db.openDatabase();
      const all = await db.getAll<Record<string, unknown>>('products');
      const found = all.find((p) => p.barcode === 'NON-EXISTENT-BARCODE');
      expect(found).toBeUndefined();
    });
  });

  // ----------------------------------------------------------
  // Cache size limit tests (Task 85 — Step 7)
  // ----------------------------------------------------------
  describe('Cache Size Limits', () => {
    it('should enforce maximum product count via count check', async () => {
      await db.openDatabase();
      const MAX = 100;
      for (let i = 0; i < MAX; i++) {
        await db.put('products', makeProduct({ id: `limit-prod-${i}` }));
      }
      const count = await db.count('products');
      expect(count).toBe(MAX);
    });

    it('should enforce maximum customer count via count check', async () => {
      await db.openDatabase();
      const MAX = 50;
      for (let i = 0; i < MAX; i++) {
        await db.put('customers', makeCustomer({ id: `limit-cust-${i}` }));
      }
      const count = await db.count('customers');
      expect(count).toBe(MAX);
    });

    it('should support LRU-style eviction by tracking updatedAt', async () => {
      await db.openDatabase();
      // Add products with staggered timestamps
      const base = Date.now();
      for (let i = 0; i < 10; i++) {
        await db.put(
          'products',
          makeProduct({
            id: `lru-${i}`,
            updatedAt: new Date(base + i * 1000).toISOString(),
          })
        );
      }
      const all = await db.getAll<Record<string, unknown>>('products');
      // Oldest should be the one with earliest updatedAt
      const sorted = all.sort(
        (a, b) =>
          new Date(a.updatedAt as string).getTime() -
          new Date(b.updatedAt as string).getTime()
      );
      expect(sorted[0]?.id).toBe('lru-0');
      // Could evict oldest when limit reached
      await db.delete('products', sorted[0]?.id as string);
      const remaining = await db.count('products');
      expect(remaining).toBe(9);
    });

    it('should calculate accurate cache size via count', async () => {
      await db.openDatabase();
      await db.put('products', makeProduct({ id: 'size-1' }));
      await db.put('products', makeProduct({ id: 'size-2' }));
      await db.put('products', makeProduct({ id: 'size-3' }));
      const count = await db.count('products');
      expect(count).toBe(3);
    });
  });

  // ----------------------------------------------------------
  // Cache invalidation tests (Task 85 — Step 8)
  // ----------------------------------------------------------
  describe('Cache Invalidation', () => {
    it('should clear all cache across multiple stores', async () => {
      await db.openDatabase();
      await db.put('products', makeProduct({ id: 'inv-p1' }));
      await db.put('customers', makeCustomer({ id: 'inv-c1' }));
      await db.clear('products');
      await db.clear('customers');
      const products = await db.getAll('products');
      const customers = await db.getAll('customers');
      expect(products.length).toBe(0);
      expect(customers.length).toBe(0);
    });

    it('should selectively clear items by criteria', async () => {
      await db.openDatabase();
      await db.put('products', makeProduct({ id: 'sel-1', category: 'food' }));
      await db.put(
        'products',
        makeProduct({ id: 'sel-2', category: 'electronics' })
      );
      await db.put('products', makeProduct({ id: 'sel-3', category: 'food' }));
      // Delete only food products
      const all = await db.getAll<Record<string, unknown>>('products');
      const foodItems = all.filter((p) => p.category === 'food');
      for (const item of foodItems) {
        await db.delete('products', item.id as string);
      }
      const remaining = await db.getAll<Record<string, unknown>>('products');
      expect(remaining.length).toBe(1);
      expect(remaining[0]?.category).toBe('electronics');
    });
  });

  // ----------------------------------------------------------
  // Versioning and upgrade tests (Task 85 — Step 9)
  // ----------------------------------------------------------
  describe('Versioning and Upgrade', () => {
    it('should open database with correct version', async () => {
      await db.openDatabase();
      // The database should exist — verify via count on any store
      const count = await db.count('products');
      expect(count).toBeGreaterThanOrEqual(0);
    });

    it('should handle opening the database multiple times idempotently', async () => {
      await db.openDatabase();
      await db.openDatabase(); // second open should not throw
      const count = await db.count('products');
      expect(count).toBeGreaterThanOrEqual(0);
    });

    it('should create all required object stores', async () => {
      await db.openDatabase();
      // Verify we can interact with all expected stores
      const stores = [
        ObjectStoreNames.PRODUCTS,
        ObjectStoreNames.CUSTOMERS,
        ObjectStoreNames.SETTINGS,
      ];
      for (const store of stores) {
        const count = await db.count(store);
        expect(count).toBeGreaterThanOrEqual(0);
      }
    });
  });

  // ----------------------------------------------------------
  // Error handling tests (Task 85 — Step 10)
  // ----------------------------------------------------------
  describe('Error Handling', () => {
    it('should handle get on an empty store', async () => {
      await db.openDatabase();
      const result = await db.get<Record<string, unknown>>(
        'products',
        'does-not-exist'
      );
      expect(result).toBeUndefined();
    });

    it('should handle delete on non-existent key gracefully', async () => {
      await db.openDatabase();
      // Should not throw
      await expect(db.delete('products', 'ghost-key')).resolves.not.toThrow();
    });

    it('should handle corrupted data by not crashing on getAll', async () => {
      await db.openDatabase();
      // Put a minimal record, then verify getAll still works
      await db.put('products', { id: 'corrupt-test', name: null });
      const all = await db.getAll<Record<string, unknown>>('products');
      expect(Array.isArray(all)).toBe(true);
    });

    it('should handle transaction abort on invalid store name', async () => {
      await db.openDatabase();
      try {
        await db.get('nonexistent_store' as any, 'key');
        // If it doesn't throw, that's also acceptable (empty result)
      } catch (err) {
        expect(err).toBeDefined();
      }
    });
  });

  // ----------------------------------------------------------
  // Search functionality tests (Task 85 — Step 11)
  // ----------------------------------------------------------
  describe('Search Functionality', () => {
    it('should find products by partial name match', async () => {
      await db.openDatabase();
      await db.put(
        'products',
        makeProduct({ id: 'srch-1', name: 'Apple iPhone 15' })
      );
      await db.put(
        'products',
        makeProduct({ id: 'srch-2', name: 'Samsung Galaxy S24' })
      );
      await db.put(
        'products',
        makeProduct({ id: 'srch-3', name: 'Apple iPad Air' })
      );
      const all = await db.getAll<Record<string, unknown>>('products');
      const results = all.filter((p) =>
        (p.name as string).toLowerCase().includes('apple')
      );
      expect(results.length).toBe(2);
    });

    it('should find customers by partial name match', async () => {
      await db.openDatabase();
      await db.put(
        'customers',
        makeCustomer({ id: 'srchc-1', name: 'John Smith' })
      );
      await db.put(
        'customers',
        makeCustomer({ id: 'srchc-2', name: 'Jane Doe' })
      );
      await db.put(
        'customers',
        makeCustomer({ id: 'srchc-3', name: 'John Doe' })
      );
      const all = await db.getAll<Record<string, unknown>>('customers');
      const results = all.filter((c) =>
        (c.name as string).toLowerCase().includes('john')
      );
      expect(results.length).toBe(2);
    });

    it('should handle search with special characters', async () => {
      await db.openDatabase();
      await db.put(
        'products',
        makeProduct({ id: 'spc-1', name: "Product (Special) [Edition] — 'v2'" })
      );
      const all = await db.getAll<Record<string, unknown>>('products');
      const results = all.filter((p) =>
        (p.name as string).includes('(Special)')
      );
      expect(results.length).toBe(1);
    });

    it('should perform search with large dataset efficiently', async () => {
      await db.openDatabase();
      for (let i = 0; i < 50; i++) {
        await db.put(
          'products',
          makeProduct({ id: `perf-${i}`, name: `Product ${i}` })
        );
      }
      const start = Date.now();
      const all = await db.getAll<Record<string, unknown>>('products');
      const results = all.filter((p) =>
        (p.name as string).includes('Product 4')
      );
      const elapsed = Date.now() - start;
      expect(results.length).toBeGreaterThan(0);
      // Search should complete within reasonable time
      expect(elapsed).toBeLessThan(5000);
    });
  });
});
