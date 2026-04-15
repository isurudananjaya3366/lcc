'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Mail, Phone, MapPin, User, Heart } from 'lucide-react';
import type { Employee } from '@/types/hr';

interface PersonalInfoTabProps {
  employee: Employee;
}

function InfoRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="grid grid-cols-3 gap-4 py-2">
      <span className="text-sm font-medium text-muted-foreground">{label}</span>
      <span className="col-span-2 text-sm">{value || '—'}</span>
    </div>
  );
}

export function PersonalInfoTab({ employee }: PersonalInfoTabProps) {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <User className="h-4 w-4" />
            Basic Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Full Name" value={`${employee.firstName} ${employee.lastName}`} />
          <Separator />
          <InfoRow label="Date of Birth" value={employee.dateOfBirth} />
          <Separator />
          <InfoRow label="Gender" value={employee.gender} />
          <Separator />
          <InfoRow label="Nationality" value={employee.nationality} />
          <Separator />
          <InfoRow label="Tax ID (NIC)" value={employee.taxId} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Mail className="h-4 w-4" />
            Contact Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Email" value={employee.email} />
          <Separator />
          <InfoRow label="Phone" value={employee.phone} />
          <Separator />
          <InfoRow label="Work Location" value={employee.workLocation} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Heart className="h-4 w-4" />
            Emergency Contact
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Name" value={employee.emergencyContact?.name} />
          <Separator />
          <InfoRow label="Relationship" value={employee.emergencyContact?.relationship} />
          <Separator />
          <InfoRow label="Phone" value={employee.emergencyContact?.phone} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <MapPin className="h-4 w-4" />
            Bank Details
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          <InfoRow label="Bank Name" value={employee.bankAccount?.bankName} />
          <Separator />
          <InfoRow label="Account Number" value={employee.bankAccount?.accountNumber} />
        </CardContent>
      </Card>
    </div>
  );
}
