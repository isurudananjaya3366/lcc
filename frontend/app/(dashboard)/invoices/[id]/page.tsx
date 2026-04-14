import type { Metadata } from 'next';
import { InvoiceDetail } from '@/components/modules/sales/Invoices/InvoiceDetail';

export const metadata: Metadata = {
  title: 'Invoice Details - LCC',
  description: 'View invoice details, line items, and payment information',
  openGraph: {
    title: 'Invoice Details - LCC',
    description: 'View invoice details, line items, and payment information',
    type: 'website',
  },
};

interface InvoiceDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function InvoiceDetailPage({ params }: InvoiceDetailPageProps) {
  const { id } = await params;
  return <InvoiceDetail invoiceId={id} />;
}
