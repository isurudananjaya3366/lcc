// ================================================================
// Products Object Store — Tasks 19 & 20
// ================================================================
// CRUD + index queries for the local products cache.
// ================================================================

import { idbService } from '../indexeddb';
import { ObjectStoreNames, type Product } from '../schema';

const STORE = ObjectStoreNames.PRODUCTS;

// ── Service ────────────────────────────────────────────────────

class ProductsService {
  // ── CRUD ─────────────────────────────────────────────────────

  async addProduct(product: Product): Promise<void> {
    await idbService.put(STORE, product);
  }

  async getProduct(productId: string): Promise<Product | undefined> {
    return idbService.get<Product>(STORE, productId);
  }

  async getAllProducts(): Promise<Product[]> {
    return idbService.getAll<Product>(STORE);
  }

  async updateProduct(
    productId: string,
    updates: Partial<Product>
  ): Promise<void> {
    const existing = await this.getProduct(productId);
    if (!existing) throw new Error(`Product ${productId} not found`);
    await idbService.put(STORE, {
      ...existing,
      ...updates,
      updated_at: new Date().toISOString(),
    });
  }

  async deleteProduct(productId: string): Promise<void> {
    await idbService.delete(STORE, productId);
  }

  async bulkAddProducts(products: Product[]): Promise<number> {
    return idbService.bulkPut(STORE, products);
  }

  async getProductCount(): Promise<number> {
    return idbService.count(STORE);
  }

  // ── Index queries (Task 20) ──────────────────────────────────

  async getProductByBarcode(barcode: string): Promise<Product | undefined> {
    return idbService.getByIndex<Product>(STORE, 'barcode', barcode);
  }

  async getProductBySKU(sku: string): Promise<Product | undefined> {
    return idbService.getByIndex<Product>(STORE, 'sku', sku);
  }

  async getProductsByCategory(categoryId: string): Promise<Product[]> {
    return idbService.getAllByIndex<Product>(STORE, 'category_id', categoryId);
  }

  async getProductsUpdatedAfter(timestamp: string): Promise<Product[]> {
    const all = await this.getAllProducts();
    return all.filter((p) => p.updated_at > timestamp);
  }

  async getActiveProducts(): Promise<Product[]> {
    return idbService.getAllByIndex<Product>(STORE, 'status', 'active');
  }

  async searchProducts(term: string): Promise<Product[]> {
    const lower = term.toLowerCase();
    const all = await this.getAllProducts();
    return all.filter(
      (p) =>
        p.name.toLowerCase().includes(lower) ||
        p.barcode?.toLowerCase().includes(lower) ||
        p.sku?.toLowerCase().includes(lower)
    );
  }

  async getMostRecentUpdate(): Promise<string | null> {
    const all = await this.getAllProducts();
    if (all.length === 0) return null;
    return all.reduce(
      (latest, p) => (p.updated_at > latest ? p.updated_at : latest),
      all[0]!.updated_at
    );
  }
}

export const productsService = new ProductsService();
