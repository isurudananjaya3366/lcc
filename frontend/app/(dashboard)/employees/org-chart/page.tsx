import { createHRMetadata } from '@/lib/metadata/hr';
import { OrgChartPage as OrgChart } from '@/components/modules/hr';

export const metadata = createHRMetadata(
  'Organization Chart',
  'View the organizational hierarchy, department structure, and reporting relationships.'
);

export default function OrgChartRoutePage() {
  return <OrgChart />;
}
