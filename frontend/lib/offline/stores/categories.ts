// ================================================================
// Categories Object Store — Task 21
// ================================================================
// CRUD + hierarchy queries for the local categories cache.
// ================================================================

import { idbService } from '../indexeddb';
import { ObjectStoreNames, type Category } from '../schema';

const STORE = ObjectStoreNames.CATEGORIES;

class CategoriesService {
  async addCategory(category: Category): Promise<void> {
    await idbService.put(STORE, category);
  }

  async getCategory(categoryId: string): Promise<Category | undefined> {
    return idbService.get<Category>(STORE, categoryId);
  }

  async getAllCategories(): Promise<Category[]> {
    return idbService.getAll<Category>(STORE);
  }

  async getCategoryBySlug(slug: string): Promise<Category | undefined> {
    return idbService.getByIndex<Category>(STORE, 'slug', slug);
  }

  async getSubcategories(parentId: string): Promise<Category[]> {
    return idbService.getAllByIndex<Category>(STORE, 'parent_id', parentId);
  }

  /** Build a full category tree (roots → children). */
  async getCategoryTree(): Promise<CategoryNode[]> {
    const all = await this.getAllCategories();
    const map = new Map<string, CategoryNode>();

    for (const cat of all) {
      map.set(cat.id, { ...cat, children: [] });
    }

    const roots: CategoryNode[] = [];
    for (const node of map.values()) {
      if (node.parent_id && map.has(node.parent_id)) {
        map.get(node.parent_id)!.children.push(node);
      } else {
        roots.push(node);
      }
    }

    return roots.sort((a, b) => a.sort_order - b.sort_order);
  }

  /** Get the path from root to a specific category. */
  async getCategoryPath(categoryId: string): Promise<Category[]> {
    const all = await this.getAllCategories();
    const map = new Map(all.map((c) => [c.id, c]));
    const path: Category[] = [];
    let current = map.get(categoryId);

    while (current) {
      path.unshift(current);
      current = current.parent_id ? map.get(current.parent_id) : undefined;
    }

    return path;
  }

  async bulkAddCategories(categories: Category[]): Promise<number> {
    return idbService.bulkPut(STORE, categories);
  }

  async getCategoryCount(): Promise<number> {
    return idbService.count(STORE);
  }

  async getMostRecentUpdate(): Promise<string | null> {
    const all = await this.getAllCategories();
    if (all.length === 0) return null;
    return all.reduce(
      (latest, c) => (c.updated_at > latest ? c.updated_at : latest),
      all[0]!.updated_at
    );
  }
}

export interface CategoryNode extends Category {
  children: CategoryNode[];
}

export const categoriesService = new CategoriesService();
