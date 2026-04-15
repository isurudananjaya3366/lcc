'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { roleSchema, type RoleFormValues } from '@/lib/validations/role';
import { RoleNameInput } from './RoleNameInput';
import { RoleDescriptionInput } from './RoleDescriptionInput';
import { PermissionMatrix } from './PermissionMatrix';

interface AddRoleModalProps {
  open: boolean;
  onClose: () => void;
  onSave?: () => void;
}

export function AddRoleModal({ open, onClose, onSave }: AddRoleModalProps) {
  const form = useForm<RoleFormValues>({
    resolver: zodResolver(roleSchema),
    defaultValues: {
      name: '',
      description: '',
      permissions: [],
    },
  });

  const isSubmitting = form.formState.isSubmitting;

  const onSubmit = async (data: RoleFormValues) => {
    // TODO: connect to API — POST /api/roles
    console.log('Create role:', data);
    form.reset();
    onSave?.();
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Add Role</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <RoleNameInput form={form} />
            <RoleDescriptionInput form={form} />

            <PermissionMatrix
              selectedIds={form.watch('permissions')}
              onChange={(ids) => form.setValue('permissions', ids)}
            />

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Creating...' : 'Create Role'}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
