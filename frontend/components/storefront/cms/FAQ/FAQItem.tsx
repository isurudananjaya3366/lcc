'use client';

import type { FAQItem as FAQItemType } from '@/types/storefront/cms.types';
import {
  AccordionItem,
  AccordionTrigger,
  AccordionContent,
} from '@/components/ui/accordion';

interface FAQItemProps {
  item: FAQItemType;
}

export function FAQItem({ item }: FAQItemProps) {
  return (
    <AccordionItem value={item.id}>
      <AccordionTrigger>{item.question}</AccordionTrigger>
      <AccordionContent>{item.answer}</AccordionContent>
    </AccordionItem>
  );
}
