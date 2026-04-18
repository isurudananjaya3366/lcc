'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProvinceDropdown } from './ProvinceDropdown';
import { DistrictDropdown } from './DistrictDropdown';
import { CityDropdown } from './CityDropdown';
import { AddressLine1Input } from './AddressLine1Input';
import { AddressLine2Input } from './AddressLine2Input';
import { LandmarkInput } from './LandmarkInput';
import { PostalCodeInput } from './PostalCodeInput';

export const AddressSection = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Shipping Address</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <ProvinceDropdown />
          <DistrictDropdown />
          <CityDropdown />
        </div>
        <AddressLine1Input />
        <AddressLine2Input />
        <LandmarkInput />
        <PostalCodeInput />
      </CardContent>
    </Card>
  );
};
