'use client';

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
import { useDepartments } from '@/hooks/hr/useEmployees';
import type { Position } from '@/types/hr';

interface PositionModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  position?: Position | null;
  onSubmit: (data: Partial<Position>) => void;
  isPending?: boolean;
}

export function PositionModal({
  open,
  onOpenChange,
  position,
  onSubmit,
  isPending,
}: PositionModalProps) {
  const isEdit = !!position;
  const { data: deptData } = useDepartments();
  const departments = deptData?.data ?? [];

  const { register, handleSubmit, reset, setValue, watch } = useForm({
    defaultValues: {
      title: position?.title ?? '',
      code: position?.code ?? '',
      description: position?.description ?? '',
      departmentId: position?.departmentId ?? '',
      level: position?.level ?? '',
      category: position?.category ?? '',
      minSalary: '',
      maxSalary: '',
    },
  });

  const departmentId = watch('departmentId');

  const handleFormSubmit = (data: Record<string, string>) => {
    onSubmit({
      title: data.title,
      code: data.code,
      description: data.description || undefined,
      departmentId: data.departmentId,
      level: data.level || undefined,
      category: data.category || undefined,
      ...(data.minSalary ? { minSalary: Number(data.minSalary) } : {}),
      ...(data.maxSalary ? { maxSalary: Number(data.maxSalary) } : {}),
    } as Partial<Position>);
    reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Edit Position' : 'Create Position'}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="pos-title">Title *</Label>
            <Input id="pos-title" {...register('title', { required: true })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="pos-code">Code *</Label>
            <Input id="pos-code" {...register('code', { required: true })} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="pos-description">Description</Label>
            <Textarea id="pos-description" {...register('description')} rows={3} />
          </div>
          <div className="space-y-2">
            <Label>Department *</Label>
            <Select value={departmentId} onValueChange={(v) => setValue('departmentId', v)}>
              <SelectTrigger>
                <SelectValue placeholder="Select department" />
              </SelectTrigger>
              <SelectContent>
                {departments.map((d) => (
                  <SelectItem key={d.id} value={d.id}>
                    {d.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="pos-level">Level</Label>
              <Input
                id="pos-level"
                type="number"
                min={1}
                placeholder="e.g., 1, 2, 3"
                {...register('level')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pos-category">Category</Label>
              <Input id="pos-category" {...register('category')} />
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="pos-minSalary">Min Salary (LKR)</Label>
              <Input
                id="pos-minSalary"
                type="number"
                min={0}
                step={1000}
                placeholder="e.g., 50000"
                {...register('minSalary')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pos-maxSalary">Max Salary (LKR)</Label>
              <Input
                id="pos-maxSalary"
                type="number"
                min={0}
                step={1000}
                placeholder="e.g., 150000"
                {...register('maxSalary')}
              />
            </div>
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
