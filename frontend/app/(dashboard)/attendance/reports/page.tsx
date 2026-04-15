import { createHRMetadata } from '@/lib/metadata/hr';
import { AttendanceReport } from '@/components/modules/hr';

export const metadata = createHRMetadata(
  'Attendance Reports',
  'Generate and view detailed attendance reports with date range selection and export options.'
);

export default function AttendanceReportsPage() {
  return <AttendanceReport />;
}
