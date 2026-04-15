import { CustomerForm } from '@/components/modules/crm/Customers/CustomerForm';
import { createCRMMetadata } from '@/lib/metadata/crm';

export const metadata = createCRMMetadata('New Customer', 'Create a new customer record');

export default function NewCustomerPage() {
  return <CustomerForm />;
}
