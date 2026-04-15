import { createHRMetadata } from '@/lib/metadata/hr';
import { LeaveRequestForm } from '@/components/modules/hr/Leave';

export const metadata = createHRMetadata(
  'Request Leave',
  'Submit a new leave request with type, dates, reason, and supporting documents.'
);

export default function LeaveRequestPage() {
  return <LeaveRequestForm />;
}
