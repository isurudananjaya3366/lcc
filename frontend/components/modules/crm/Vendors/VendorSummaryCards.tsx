'use client';

import { Building2, CheckCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { useVendors } from '@/hooks/crm/useVendors';

export function VendorSummaryCards() {
  const { data, isLoading } = useVendors();

  const vendors = data?.data ?? [];
  const total = data?.pagination?.totalCount ?? vendors.length;
  const active = vendors.filter((v) => v.isActive).length;

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {Array.from({ length: 2 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
            <Building2 className="h-4 w-4 text-blue-500" />
            Total Vendors
          </div>
          <p className="text-2xl font-bold">{total}</p>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
            <CheckCircle className="h-4 w-4 text-green-500" />
            Active Vendors
          </div>
          <p className="text-2xl font-bold">{active}</p>
        </CardContent>
      </Card>
    </div>
  );
}
