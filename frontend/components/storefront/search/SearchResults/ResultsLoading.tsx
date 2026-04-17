import { LoadingGridSkeleton } from '@/components/storefront/catalog';

interface ResultsLoadingProps {
  count?: number;
  className?: string;
}

export function ResultsLoading({ count = 8, className }: ResultsLoadingProps) {
  return (
    <LoadingGridSkeleton
      count={count}
      columns={4}
      className={className}
    />
  );
}
