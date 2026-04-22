'use client';

import { useState, useMemo } from 'react';
import Link from 'next/link';
import { Plus, FolderTree, List, LayoutGrid, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { CategoryTree, DeleteCategoryDialog } from '@/components/modules/products/Categories';
import type { ProductCategory } from '@/types/product';

// TODO: Replace with API data
const MOCK_CATEGORIES: ProductCategory[] = [
  {
    id: '1',
    name: 'Electronics',
    slug: 'electronics',
    description: 'Electronic devices and accessories',
    displayOrder: 1,
    isActive: true,
    productCount: 45,
  },
  {
    id: '2',
    name: 'Smartphones',
    slug: 'smartphones',
    parentId: '1',
    displayOrder: 1,
    isActive: true,
    productCount: 20,
  },
  {
    id: '3',
    name: 'Laptops',
    slug: 'laptops',
    parentId: '1',
    displayOrder: 2,
    isActive: true,
    productCount: 15,
  },
  {
    id: '4',
    name: 'Clothing',
    slug: 'clothing',
    description: 'Apparel and fashion items',
    displayOrder: 2,
    isActive: true,
    productCount: 80,
  },
  {
    id: '5',
    name: 'Men',
    slug: 'men',
    parentId: '4',
    displayOrder: 1,
    isActive: true,
    productCount: 35,
  },
  {
    id: '6',
    name: 'Women',
    slug: 'women',
    parentId: '4',
    displayOrder: 2,
    isActive: true,
    productCount: 40,
  },
  {
    id: '7',
    name: 'Accessories',
    slug: 'accessories',
    displayOrder: 3,
    isActive: false,
    productCount: 0,
  },
];

interface CategoryWithChildren {
  id: string;
  name: string;
  slug: string;
  description?: string;
  parentId?: string;
  imageUrl?: string;
  displayOrder: number;
  isActive: boolean;
  productCount: number;
  children: CategoryWithChildren[];
}

function buildCategoryTree(categories: ProductCategory[]): CategoryWithChildren[] {
  const map = new Map<string, CategoryWithChildren>();
  const roots: CategoryWithChildren[] = [];

  for (const cat of categories) {
    map.set(cat.id, { ...cat, children: [] });
  }

  for (const cat of categories) {
    const node = map.get(cat.id)!;
    if (cat.parentId && map.has(cat.parentId)) {
      map.get(cat.parentId)!.children.push(node);
    } else {
      roots.push(node);
    }
  }

  return roots;
}

export function CategoryListView() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [deleteCategory, setDeleteCategory] = useState<ProductCategory | null>(null);

  const categories = MOCK_CATEGORIES;

  const filtered = useMemo(() => {
    let result = categories;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (c) => c.name.toLowerCase().includes(q) || c.slug.toLowerCase().includes(q)
      );
    }
    if (statusFilter === 'active') result = result.filter((c) => c.isActive);
    if (statusFilter === 'inactive') result = result.filter((c) => !c.isActive);
    return result;
  }, [categories, search, statusFilter]);

  const tree = useMemo(() => buildCategoryTree(filtered), [filtered]);

  const totalCategories = categories.length;
  const activeCategories = categories.filter((c) => c.isActive).length;
  const rootCategories = categories.filter((c) => !c.parentId).length;

  const handleEdit = (id: string) => {
    window.location.href = `/products/categories/${id}`;
  };

  const handleDelete = (id: string) => {
    const cat = categories.find((c) => c.id === id);
    if (cat) setDeleteCategory(cat);
  };

  const handleDeleteConfirm = () => {
    // TODO: Call API to delete category
    setDeleteCategory(null);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Categories</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Organize products into hierarchical categories
          </p>
        </div>
        <Button asChild>
          <Link href="/products/categories/new">
            <Plus className="mr-2 h-4 w-4" />
            Add Category
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search categories..."
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[140px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Category Tree */}
      <Card>
        <div className="border-b px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FolderTree className="h-4 w-4 text-muted-foreground" />
              <h3 className="text-sm font-medium">Category Hierarchy</h3>
            </div>
            <span className="text-xs text-muted-foreground">{totalCategories} categories</span>
          </div>
        </div>
        <CardContent className="p-0">
          {tree.length > 0 ? (
            <CategoryTree
              categories={tree}
              onEdit={handleEdit}
              onDelete={handleDelete}
              expandedByDefault
            />
          ) : (
            <div className="flex flex-col items-center justify-center py-16">
              <FolderTree className="h-12 w-12 text-muted-foreground/30" />
              <h3 className="mt-4 text-sm font-medium">No Categories</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                {search || statusFilter !== 'all'
                  ? 'No categories match your filters.'
                  : 'Create categories to organize your products.'}
              </p>
              {!search && statusFilter === 'all' && (
                <Button asChild className="mt-4">
                  <Link href="/products/categories/new">
                    <Plus className="mr-2 h-4 w-4" />
                    Add First Category
                  </Link>
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Total Categories</p>
            <p className="mt-1 text-2xl font-bold">{totalCategories}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Active Categories</p>
            <p className="mt-1 text-2xl font-bold text-green-600 dark:text-green-400">
              {activeCategories}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">Root Categories</p>
            <p className="mt-1 text-2xl font-bold">{rootCategories}</p>
          </CardContent>
        </Card>
      </div>

      <DeleteCategoryDialog
        category={deleteCategory}
        isOpen={!!deleteCategory}
        onClose={() => setDeleteCategory(null)}
        onConfirm={handleDeleteConfirm}
        categories={categories}
      />
    </div>
  );
}
