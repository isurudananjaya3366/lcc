'use client';

import { useEffect, useMemo, useState } from 'react';

import type { FAQItem } from '@/types/storefront/cms.types';
import { getFAQItems } from '@/services/storefront/cmsService';
import { PageLayout, PageHeader } from '@/components/storefront/cms/Layout';
import { FAQSearch } from './FAQSearch';
import { FAQCategories } from './FAQCategories';
import { FAQAccordion } from './FAQAccordion';

export function FAQPage() {
  const [items, setItems] = useState<FAQItem[]>([]);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  useEffect(() => {
    getFAQItems().then(setItems);
  }, []);

  const categories = useMemo(
    () => Array.from(new Set(items.map((i) => i.category))),
    [items],
  );

  const filtered = useMemo(() => {
    let result = items;
    if (selectedCategory !== 'All') {
      result = result.filter((i) => i.category === selectedCategory);
    }
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(
        (i) =>
          i.question.toLowerCase().includes(q) ||
          i.answer.toLowerCase().includes(q),
      );
    }
    return result;
  }, [items, selectedCategory, search]);

  return (
    <PageLayout>
      <PageHeader
        title="Frequently Asked Questions"
        breadcrumbs={[
          { label: 'Home', href: '/' },
          { label: 'FAQ' },
        ]}
      />
      <FAQSearch value={search} onChange={setSearch} />
      <FAQCategories
        categories={categories}
        selected={selectedCategory}
        onSelect={setSelectedCategory}
      />
      <FAQAccordion items={filtered} />
    </PageLayout>
  );
}
