'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Form } from '@/components/ui/form';
import { roleSchema, type RoleFormValues } from '@/lib/validations/role';
import { RoleNameInput } from '@/components/modules/settings/Roles/RoleNameInput';
import { RoleDescriptionInput } from '@/components/modules/settings/Roles/RoleDescriptionInput';
import { PermissionMatrix } from '@/components/modules/settings/Roles/PermissionMatrix';

interface EditRoleFormProps {
  roleId: string;
}

// Placeholder — will be replaced with API data
const MOCK_ROLE = {
  name: 'Custom Role',
  description: 'A custom role',
  permissions: [] as string[],
  isSystem: false,
};

function EditRoleForm({ roleId }: EditRoleFormProps) {
  const form = useForm<RoleFormValues>({
    resolver: zodResolver(roleSchema),
    defaultValues: {
      name: MOCK_ROLE.name,
      description: MOCK_ROLE.description,
      permissions: MOCK_ROLE.permissions,
    },
  });

  const isSubmitting = form.formState.isSubmitting;

  const onSubmit = async (data: RoleFormValues) => {
    // TODO: connect to API — PATCH /api/roles/{roleId}
    console.log('Update role:', { roleId, ...data });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/settings/roles">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Edit Role</h2>
          <p className="text-muted-foreground">Settings &gt; Roles &gt; Edit Role</p>
        </div>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <RoleNameInput form={form} />
          <RoleDescriptionInput form={form} />

          <PermissionMatrix
            selectedIds={form.watch('permissions')}
            onChange={(ids) => form.setValue('permissions', ids)}
          />

          <div className="flex justify-end gap-2">
            <Button variant="outline" asChild>
              <Link href="/settings/roles">Cancel</Link>
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              <Save className="mr-2 h-4 w-4" />
              {isSubmitting ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </form>
      </Form>
    </div>
  );
}

export default async function EditRolePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <EditRoleForm roleId={id} />;
}
