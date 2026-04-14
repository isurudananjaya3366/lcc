import type { Metadata } from 'next';
import { QuoteDetail } from '@/components/modules/sales/Quotes/QuoteDetail';

export const metadata: Metadata = {
  title: 'Quote Details - LCC',
  description: 'View quote details, line items, and pricing',
  openGraph: {
    title: 'Quote Details - LCC',
    description: 'View quote details, line items, and pricing',
    type: 'website',
  },
};

interface QuoteDetailPageProps {
  params: Promise<{ id: string }>;
}

export default async function QuoteDetailPage({ params }: QuoteDetailPageProps) {
  const { id } = await params;
  return <QuoteDetail quoteId={id} />;
}
