'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { PersonalInfoSection } from './PersonalInfoSection';
import { ContactInfoSection } from './ContactInfoSection';
import { EmploymentInfoSection } from './EmploymentInfoSection';
import { DocumentUploadSection } from './DocumentUploadSection';
import { useCreateEmployee } from '@/hooks/hr/useEmployees';
import { employeeFormSchema, type EmployeeFormValues } from '@/lib/validations/employee';
import { EmploymentType } from '@/types/hr';

export function EmployeeForm() {
  const router = useRouter();
  const createMutation = useCreateEmployee();
  const [documents, setDocuments] = useState<Record<string, File | null>>({});

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<EmployeeFormValues>({
    resolver: zodResolver(employeeFormSchema),
    defaultValues: {
      firstName: '',
      lastName: '',
      email: '',
      phone: '',
      nic: '',
      dateOfBirth: '',
      gender: '',
      nationality: '',
      employmentType: EmploymentType.FULL_TIME,
      departmentId: '',
      positionId: '',
      hireDate: '',
      probationEndDate: '',
      managerId: '',
      workLocation: '',
      addressLine1: '',
      addressLine2: '',
      city: '',
      district: '',
      emergencyContactName: '',
      emergencyContactRelationship: '',
      emergencyContactPhone: '',
      bankName: '',
      bankAccountNumber: '',
      taxId: '',
      salary: undefined,
    },
  });

  const gender = watch('gender');
  const employmentType = watch('employmentType');
  const departmentId = watch('departmentId');
  const positionId = watch('positionId');
  const managerId = watch('managerId');

  const handleFileChange = (field: string, file: File | null) => {
    setDocuments((prev) => ({ ...prev, [field]: file }));
  };

  const onSubmit = (data: EmployeeFormValues) => {
    createMutation.mutate(data, {
      onSuccess: () => router.push('/employees'),
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Add Employee</h1>
          <p className="text-muted-foreground">Create a new employee record</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="max-w-3xl space-y-6">
        <PersonalInfoSection
          register={register}
          errors={errors}
          setValue={setValue}
          gender={gender}
        />
        <ContactInfoSection
          register={register}
          errors={errors}
          setValue={setValue}
          district={watch('district')}
        />
        <EmploymentInfoSection
          register={register}
          errors={errors}
          setValue={setValue}
          employmentType={employmentType}
          departmentId={departmentId}
          positionId={positionId}
          managerId={managerId}
        />
        <DocumentUploadSection documents={documents} onFileChange={handleFileChange} />

        <div className="flex gap-3 pt-2">
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Creating...' : 'Create Employee'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
