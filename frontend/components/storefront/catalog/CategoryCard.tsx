import Image from 'next/image';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import type { StoreCategory } from '@/types/store/category';

interface CategoryCardProps {
  category: StoreCategory;
  className?: string;
}

export function CategoryCard({ category, className }: CategoryCardProps) {
  return (
    <Link
      href={`/products/category/${category.slug}`}
      className={cn(
        'group relative flex flex-col overflow-hidden rounded-xl border border-gray-200',
        'bg-white transition-all duration-300 hover:shadow-lg hover:border-gray-300',
        className
      )}
    >
      {/* Image */}
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-gray-100">
        {category.image ? (
          <Image
            src={category.image}
            alt={category.name}
            fill
            className="object-cover transition-transform duration-300 group-hover:scale-105"
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 25vw"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
            {/* Folder icon */}
            <svg
              className="h-10 w-10 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M2.25 12.75V12A2.25 2.25 0 0 1 4.5 9.75h15A2.25 2.25 0 0 1 21.75 12v.75m-8.69-6.44-2.12-2.12a1.5 1.5 0 0 0-1.061-.44H4.5A2.25 2.25 0 0 0 2.25 6v12a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9a2.25 2.25 0 0 0-2.25-2.25h-5.379a1.5 1.5 0 0 1-1.06-.44Z"
              />
            </svg>
          </div>
        )}

        {/* Product count badge */}
        <span className="absolute bottom-2 right-2 rounded-full bg-black/60 px-2.5 py-0.5 text-xs font-medium text-white backdrop-blur-sm">
          {category.productCount} {category.productCount === 1 ? 'item' : 'items'}
        </span>
      </div>

      {/* Content */}
      <div className="flex flex-1 flex-col p-3 sm:p-4">
        <h3 className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors sm:text-base">
          {category.name}
        </h3>
        {category.description && (
          <p className="mt-1 text-xs text-gray-500 line-clamp-2">{category.description}</p>
        )}
      </div>
    </Link>
  );
}
