import { createHRMetadata } from '@/lib/metadata/hr';
import { PayrollRunPage as PayrollRunWizard } from '@/components/modules/hr/Payroll';

export const metadata = createHRMetadata(
  'Run Payroll',
  'Process payroll — select period, choose employees, review calculations, and confirm processing.'
);

export default function PayrollRunPage() {
  return <PayrollRunWizard />;
}
