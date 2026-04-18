import type { Metadata } from 'next';
import { AddressesPage } from '@/components/storefront/portal/Addresses';

export const metadata: Metadata = {
  title: 'My Addresses',
};

export default function Addresses() {
  return <AddressesPage />;
}
