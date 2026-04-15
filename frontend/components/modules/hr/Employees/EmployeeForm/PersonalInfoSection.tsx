'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { UseFormRegister, FieldErrors, UseFormSetValue } from 'react-hook-form';
import type { EmployeeFormValues } from '@/lib/validations/employee';

interface PersonalInfoSectionProps {
  register: UseFormRegister<EmployeeFormValues>;
  errors: FieldErrors<EmployeeFormValues>;
  setValue: UseFormSetValue<EmployeeFormValues>;
  gender?: string;
}

export function PersonalInfoSection({
  register,
  errors,
  setValue,
  gender,
}: PersonalInfoSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Personal Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="firstName">First Name *</Label>
            <Input id="firstName" {...register('firstName')} />
            {errors.firstName && (
              <p className="text-xs text-destructive">{errors.firstName.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="lastName">Last Name *</Label>
            <Input id="lastName" {...register('lastName')} />
            {errors.lastName && (
              <p className="text-xs text-destructive">{errors.lastName.message}</p>
            )}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="nic">NIC Number</Label>
            <Input id="nic" placeholder="e.g., 199012345678" {...register('nic')} />
            {errors.nic && <p className="text-xs text-destructive">{errors.nic.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="dateOfBirth">Date of Birth</Label>
            <Input id="dateOfBirth" type="date" {...register('dateOfBirth')} />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label>Gender</Label>
            <Select value={gender ?? ''} onValueChange={(v) => setValue('gender', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="MALE">Male</SelectItem>
                <SelectItem value="FEMALE">Female</SelectItem>
                <SelectItem value="OTHER">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="nationality">Nationality</Label>
            <Input id="nationality" placeholder="e.g., Sri Lankan" {...register('nationality')} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
