import { cn } from '@/lib/utils';
import { Breadcrumb, type BreadcrumbItem } from './Breadcrumb';
import { CatalogTitle } from './CatalogTitle';
import { ProductCount } from './ProductCount';

interface CatalogHeaderProps {
  breadcrumbs: BreadcrumbItem[];
  title: string;
  productCount?: number;
  isLoading?: boolean;
  className?: string;
}

export function CatalogHeader({
  breadcrumbs,
  title,
  productCount,
  isLoading,
  className,
}: CatalogHeaderProps) {
  return (
    <div className={cn('border-b pb-6 mb-8', className)}>
      <Breadcrumb items={breadcrumbs} className="mb-4" />
      <CatalogTitle title={title} />
      <ProductCount count={productCount} isLoading={isLoading} className="mt-2" />
    </div>
  );
}
