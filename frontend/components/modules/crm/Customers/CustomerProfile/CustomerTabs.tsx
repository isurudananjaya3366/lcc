'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { OverviewTab } from './OverviewTab';
import { OrdersTab } from './OrdersTab';
import { InvoicesTab } from './InvoicesTab';
import { CommunicationTab } from './CommunicationTab';
import type { Customer } from '@/types/customer';

interface CustomerTabsProps {
  customerId: string;
  customer?: Customer;
  defaultTab?: string;
  onTabChange?: (tab: string) => void;
  onEdit?: () => void;
  onAdjustCredit?: () => void;
}

export function CustomerTabs({
  customerId,
  customer,
  defaultTab = 'overview',
  onTabChange,
  onEdit,
  onAdjustCredit,
}: CustomerTabsProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();
  const activeTab = searchParams.get('tab') || defaultTab;

  function handleTabChange(tab: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (tab === 'overview') {
      params.delete('tab');
    } else {
      params.set('tab', tab);
    }
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    onTabChange?.(tab);
  }

  return (
    <Tabs value={activeTab} onValueChange={handleTabChange}>
      <TabsList>
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="orders" className="gap-1">
          Orders
          {customer && customer.totalOrders > 0 && (
            <Badge variant="secondary" className="ml-1 h-5 px-1.5 text-xs">
              {customer.totalOrders}
            </Badge>
          )}
        </TabsTrigger>
        <TabsTrigger value="invoices">Invoices</TabsTrigger>
        <TabsTrigger value="communication">Communication</TabsTrigger>
        <TabsTrigger value="notes">Notes</TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="mt-6">
        <OverviewTab
          customerId={customerId}
          customer={customer}
          onEdit={onEdit}
          onAdjustCredit={onAdjustCredit}
        />
      </TabsContent>

      <TabsContent value="orders" className="mt-6">
        <OrdersTab customerId={customerId} />
      </TabsContent>

      <TabsContent value="invoices" className="mt-6">
        <InvoicesTab customerId={customerId} />
      </TabsContent>

      <TabsContent value="communication" className="mt-6">
        <CommunicationTab customerId={customerId} />
      </TabsContent>

      <TabsContent value="notes" className="mt-6">
        <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
          <p>Notes feature will be available soon.</p>
        </div>
      </TabsContent>
    </Tabs>
  );
}
