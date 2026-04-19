'use client';

import type { FAQItem as FAQItemType } from '@/types/storefront/cms.types';
import { Accordion } from '@/components/ui/accordion';
import { FAQItem } from './FAQItem';

interface FAQAccordionProps {
  items: FAQItemType[];
}

export function FAQAccordion({ items }: FAQAccordionProps) {
  if (items.length === 0) {
    return (
      <p className="py-8 text-center text-muted-foreground">
        No matching questions found.
      </p>
    );
  }

  return (
    <Accordion type="single" collapsible className="w-full">
      {items.map((item) => (
        <FAQItem key={item.id} item={item} />
      ))}
    </Accordion>
  );
}
