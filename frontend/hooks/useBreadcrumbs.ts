'use client';

import { useMemo } from 'react';
import { usePathname } from 'next/navigation';
import { getRouteLabel, isDynamicSegment } from '@/lib/navigation';
import type { BreadcrumbItemData } from '@/components/layout/Breadcrumb';

/**
 * Build breadcrumb items from the current pathname.
 *
 * Dynamic segments (numeric IDs, UUIDs) are shown with a
 * generic "Details" label.  A real implementation can fetch
 * entity names via React Query / SWR.
 */
export function useBreadcrumbs(): BreadcrumbItemData[] {
  const pathname = usePathname();

  return useMemo(() => {
    const segments = pathname.split('/').filter(Boolean);
    if (segments.length === 0) return [];

    const items: BreadcrumbItemData[] = [];

    for (let i = 0; i < segments.length; i++) {
      const segment = segments[i];
      if (!segment) continue;
      const href = '/' + segments.slice(0, i + 1).join('/');
      const isCurrent = i === segments.length - 1;
      const label = isDynamicSegment(segment) ? 'Details' : getRouteLabel(segment);

      items.push({ label, href, isCurrent });
    }

    return items;
  }, [pathname]);
}
