import { Breadcrumb, type BreadcrumbItem } from '@/components/storefront/catalog/Breadcrumb';

interface ProductBreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function ProductBreadcrumb({ items, className }: ProductBreadcrumbProps) {
  return <Breadcrumb items={items} className={className} />;
}
