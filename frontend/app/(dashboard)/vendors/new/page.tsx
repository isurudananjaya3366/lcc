import { VendorForm } from '@/components/modules/crm/Vendors/VendorForm';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata('New Vendor', 'Add a new vendor or supplier');

export default function NewVendorPage() {
  return <VendorForm />;
}
