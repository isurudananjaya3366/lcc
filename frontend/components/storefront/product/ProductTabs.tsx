'use client';

import { useState } from 'react';
import { TabNavigation } from './TabNavigation';
import { TabPanel } from './TabPanel';
import { DescriptionTab } from './DescriptionTab';
import { SpecificationsTab } from './SpecificationsTab';
import { ReviewsTab } from './ReviewsTab';

interface ProductTabsProps {
  description: string;
  specifications?: Record<string, string>;
  productId: number;
  reviewCount: number;
}

export type TabId = 'description' | 'specifications' | 'reviews';

interface Tab {
  id: TabId;
  label: string;
  badge?: number;
}

export function ProductTabs({
  description,
  specifications,
  productId,
  reviewCount,
}: ProductTabsProps) {
  const [activeTab, setActiveTab] = useState<TabId>('description');

  const tabs: Tab[] = [
    { id: 'description', label: 'Description' },
    { id: 'specifications', label: 'Specifications' },
    { id: 'reviews', label: 'Reviews', badge: reviewCount },
  ];

  return (
    <div id="product-reviews">
      <TabNavigation tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      <TabPanel isActive={activeTab === 'description'}>
        <DescriptionTab description={description} />
      </TabPanel>

      <TabPanel isActive={activeTab === 'specifications'}>
        <SpecificationsTab specifications={specifications} />
      </TabPanel>

      <TabPanel isActive={activeTab === 'reviews'}>
        <ReviewsTab productId={productId} />
      </TabPanel>
    </div>
  );
}
