import type { Metadata } from 'next';
import { TermsPage } from '@/components/storefront/cms/Policy';

export const metadata: Metadata = {
  title: 'Terms & Conditions',
};

export default function TermsRoute() {
  return <TermsPage />;
}
