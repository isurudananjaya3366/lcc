'use client';

import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { useCallback } from 'react';
import { Pagination } from '@/components/storefront/catalog';

interface ResultsPaginationProps {
  currentPage: number;
  totalPages: number;
  totalItems?: number;
  className?: string;
}

const PAGE_SIZE = 12;

export function ResultsPagination({
  currentPage,
  totalPages,
  totalItems,
  className,
}: ResultsPaginationProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const handlePageChange = useCallback(
    (page: number) => {
      const params = new URLSearchParams(searchParams.toString());
      if (page <= 1) {
        params.delete('page');
      } else {
        params.set('page', String(page));
      }
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, searchParams, pathname],
  );

  if (totalPages <= 1) return null;

  return (
    <Pagination
      currentPage={currentPage}
      totalPages={totalPages}
      onPageChange={handlePageChange}
      pageSize={PAGE_SIZE}
      totalItems={totalItems}
      className={className}
    />
  );
}
