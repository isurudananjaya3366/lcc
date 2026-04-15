import { createHRMetadata } from '@/lib/metadata/hr';
import { EmployeeForm } from '@/components/modules/hr/Employees';

export const metadata = createHRMetadata(
  'Add Employee',
  'Create a new employee record with personal, contact, and employment information.'
);

export default function NewEmployeePage() {
  return <EmployeeForm />;
}
