import type { Metadata } from 'next';
import { NewOrderForm } from '@/components/modules/sales/Orders/NewOrderForm';

export const metadata: Metadata = {
  title: 'Create New Order - LCC',
  description: 'Create a new customer order',
  openGraph: {
    title: 'Create New Order - LCC',
    description: 'Create a new customer order',
    type: 'website',
  },
};

export default function NewOrderPage() {
  return <NewOrderForm />;
}
