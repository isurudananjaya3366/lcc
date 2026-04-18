'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FirstNameInput } from './FirstNameInput';
import { LastNameInput } from './LastNameInput';

export const PersonalInfoSection = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Personal Information</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <FirstNameInput />
          <LastNameInput />
        </div>
      </CardContent>
    </Card>
  );
};
