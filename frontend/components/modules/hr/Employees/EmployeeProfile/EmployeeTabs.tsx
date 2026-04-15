'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PersonalInfoTab } from './PersonalInfoTab';
import { EmploymentInfoTab } from './EmploymentInfoTab';
import type { Employee } from '@/types/hr';

interface EmployeeTabsProps {
  employee: Employee;
  defaultTab?: string;
}

export function EmployeeTabs({ employee, defaultTab = 'personal' }: EmployeeTabsProps) {
  return (
    <Tabs defaultValue={defaultTab} className="w-full">
      <TabsList>
        <TabsTrigger value="personal">Personal</TabsTrigger>
        <TabsTrigger value="employment">Employment</TabsTrigger>
        <TabsTrigger value="documents" disabled>
          Documents
        </TabsTrigger>
        <TabsTrigger value="performance" disabled>
          Performance
        </TabsTrigger>
      </TabsList>

      <TabsContent value="personal" className="mt-6">
        <PersonalInfoTab employee={employee} />
      </TabsContent>

      <TabsContent value="employment" className="mt-6">
        <EmploymentInfoTab employee={employee} />
      </TabsContent>

      <TabsContent value="documents" className="mt-6">
        <p className="text-muted-foreground">
          Document management will be implemented in a future release.
        </p>
      </TabsContent>

      <TabsContent value="performance" className="mt-6">
        <p className="text-muted-foreground">
          Performance tracking will be implemented in a future release.
        </p>
      </TabsContent>
    </Tabs>
  );
}
