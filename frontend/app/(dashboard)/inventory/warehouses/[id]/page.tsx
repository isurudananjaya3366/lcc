import type { Metadata } from 'next';
import { EditWarehouseClient } from './EditWarehouseClient';

export const metadata: Metadata = {
  title: 'Edit Warehouse - LCC',
  description: 'Edit warehouse details and settings',
  openGraph: {
    title: 'Edit Warehouse - LCC',
    description: 'Edit warehouse details and settings',
    type: 'website',
  },
};

export default function EditWarehousePage({ params }: { params: { id: string } }) {
  return <EditWarehouseClient warehouseId={params.id} />;
}
