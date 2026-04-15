import { Suspense } from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { createHRMetadata } from '@/lib/metadata/hr';
import { EmployeeDetails } from '@/components/modules/hr';

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return createHRMetadata(
    `Employee ${id}`,
    'View employee profile, personal details, employment information, and documents.'
  );
}

export default async function EmployeeDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  return (
    <Suspense
      fallback={
        <div className="space-y-6">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-64 w-full" />
        </div>
      }
    >
      <EmployeeDetails employeeId={id} />
    </Suspense>
  );
}
