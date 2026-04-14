import type { Metadata } from 'next';
import { NewQuoteForm } from '@/components/modules/sales/Quotes/NewQuoteForm';

export const metadata: Metadata = {
  title: 'Create New Quote - LCC',
  description: 'Create a new sales quote',
  openGraph: {
    title: 'Create New Quote - LCC',
    description: 'Create a new sales quote',
    type: 'website',
  },
};

export default function NewQuotePage() {
  return <NewQuoteForm />;
}
