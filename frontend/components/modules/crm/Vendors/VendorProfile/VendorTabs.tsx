'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { OverviewTab } from './OverviewTab';
import { ProductsTab } from './ProductsTab';
import { POHistoryTab } from './POHistoryTab';
import type { Vendor } from '@/types/vendor';

interface VendorTabsProps {
  vendorId: string;
  vendor: Vendor;
}

export function VendorTabs({ vendorId, vendor }: VendorTabsProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const activeTab = searchParams.get('tab') || 'overview';

  function handleTabChange(tab: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (tab === 'overview') {
      params.delete('tab');
    } else {
      params.set('tab', tab);
    }
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }

  return (
    <Tabs value={activeTab} onValueChange={handleTabChange}>
      <TabsList>
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="products">Products</TabsTrigger>
        <TabsTrigger value="po-history">PO History</TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="mt-6">
        <OverviewTab vendor={vendor} />
      </TabsContent>

      <TabsContent value="products" className="mt-6">
        <ProductsTab vendorId={vendorId} />
      </TabsContent>

      <TabsContent value="po-history" className="mt-6">
        <POHistoryTab vendorId={vendorId} />
      </TabsContent>
    </Tabs>
  );
}
