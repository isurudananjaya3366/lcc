import { POForm } from '@/components/modules/crm/PurchaseOrders/POForm';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata('New Purchase Order', 'Create a new purchase order');

export default function NewPOPage() {
  return <POForm />;
}
