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

const SL_DISTRICTS = [
  'Ampara',
  'Anuradhapura',
  'Badulla',
  'Batticaloa',
  'Colombo',
  'Galle',
  'Gampaha',
  'Hambantota',
  'Jaffna',
  'Kalutara',
  'Kandy',
  'Kegalle',
  'Kilinochchi',
  'Kurunegala',
  'Mannar',
  'Matale',
  'Matara',
  'Monaragala',
  'Mullaitivu',
  'Nuwara Eliya',
  'Polonnaruwa',
  'Puttalam',
  'Ratnapura',
  'Trincomalee',
  'Vavuniya',
];

interface ContactInfoSectionProps {
  register: UseFormRegister<EmployeeFormValues>;
  errors: FieldErrors<EmployeeFormValues>;
  setValue: UseFormSetValue<EmployeeFormValues>;
  district?: string;
}

export function ContactInfoSection({
  register,
  errors,
  setValue,
  district,
}: ContactInfoSectionProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Contact Information</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="email">Email *</Label>
            <Input id="email" type="email" {...register('email')} />
            {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Phone</Label>
            <Input id="phone" placeholder="0711234567" {...register('phone')} />
            {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="addressLine1">Address Line 1</Label>
            <Input id="addressLine1" {...register('addressLine1')} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="addressLine2">Address Line 2</Label>
            <Input id="addressLine2" {...register('addressLine2')} />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="city">City</Label>
            <Input id="city" {...register('city')} />
          </div>
          <div className="space-y-2">
            <Label>District</Label>
            <Select value={district ?? ''} onValueChange={(v) => setValue('district', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select district" />
              </SelectTrigger>
              <SelectContent>
                {SL_DISTRICTS.map((d) => (
                  <SelectItem key={d} value={d}>
                    {d}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="border-t pt-4">
          <h4 className="mb-3 text-sm font-medium">Emergency Contact</h4>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <Label htmlFor="emergencyContactName">Name</Label>
              <Input id="emergencyContactName" {...register('emergencyContactName')} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="emergencyContactRelationship">Relationship</Label>
              <Input
                id="emergencyContactRelationship"
                {...register('emergencyContactRelationship')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="emergencyContactPhone">Phone</Label>
              <Input
                id="emergencyContactPhone"
                placeholder="0711234567"
                {...register('emergencyContactPhone')}
              />
              {errors.emergencyContactPhone && (
                <p className="text-xs text-destructive">{errors.emergencyContactPhone.message}</p>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
