import { cn } from '@/lib/utils';
import type { StoreCategory } from '@/types/store/category';
import { CategoryCard } from './CategoryCard';

interface SubcategoryGridProps {
  categories: StoreCategory[];
  className?: string;
}

export function SubcategoryGrid({ categories, className }: SubcategoryGridProps) {
  if (!categories.length) return null;

  return (
    <section className={cn('w-full', className)}>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 sm:text-xl">Browse Subcategories</h2>
        <span className="text-sm text-gray-500">
          {categories.length} {categories.length === 1 ? 'subcategory' : 'subcategories'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {categories.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </section>
  );
}
