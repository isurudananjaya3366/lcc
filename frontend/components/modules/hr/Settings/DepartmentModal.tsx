'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useDepartments, useEmployees } from '@/hooks/hr/useEmployees';
import type { Department } from '@/types/hr';

interface DepartmentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  department?: Department | null;
  onSubmit: (data: Partial<Department>) => void;
  isPending?: boolean;
}

export function DepartmentModal({
  open,
  onOpenChange,
  department,
  onSubmit,
  isPending,
}: DepartmentModalProps) {
  const isEdit = !!department;
  const { data: deptData } = useDepartments();
  const { data: empData } = useEmployees({});
  const departments = deptData?.data ?? [];
  const employees = empData?.data ?? [];

  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      name: department?.name ?? '',
      code: department?.code ?? '',
      description: department?.description ?? '',
      managerId: department?.managerId ?? '',
      parentDepartmentId: department?.parentDepartmentId ?? '',
    },
  });

  const parentId = watch('parentDepartmentId');

  const handleFormSubmit = (data: Record<string, string>) => {
    onSubmit({
      name: data.name,
      code: data.code,
      description: data.description || undefined,
      managerId: data.managerId || undefined,
      parentDepartmentId: data.parentDepartmentId || undefined,
    });
    reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit Department' : 'Create Department'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="dept-name">Name *</Label>
            <Input id="dept-name" {...register('name', { required: true })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dept-code">Code *</Label>
            <Input id="dept-code" {...register('code', { required: true })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dept-description">Description</Label>
            <Textarea id="dept-description" {...register('description')} rows={3} />
          </div>
          <div className="space-y-2">
            <Label>Parent Department</Label>
            <Select
              value={parentId ?? ''}
              onValueChange={(v) => setValue('parentDepartmentId', v === '__none__' ? '' : v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="None" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__none__">None</SelectItem>
                {departments
                  .filter((d) => d.id !== department?.id)
                  .map((d) => (
                    <SelectItem key={d.id} value={d.id}>
                      {d.name}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Department Head</Label>
            <Select
              value={watch('managerId') ?? ''}
              onValueChange={(v) => setValue('managerId', v === '__none__' ? '' : v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select head" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="__none__">None</SelectItem>
                {employees.map((e) => (
                  <SelectItem key={e.id} value={e.id}>
                    {e.firstName} {e.lastName} ({e.employeeNumber})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? 'Saving...' : isEdit ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
