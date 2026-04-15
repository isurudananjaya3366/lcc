'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Pencil, Trash2, Search } from 'lucide-react';
import { DepartmentModal } from './DepartmentModal';
import { useDepartments } from '@/hooks/hr/useEmployees';
import employeeService from '@/services/api/employeeService';
import type { Department } from '@/types/hr';

export function DepartmentManagement() {
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editDept, setEditDept] = useState<Department | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = useDepartments();
  const departments = data?.data ?? [];

  const filtered = departments.filter((d) => d.name.toLowerCase().includes(search.toLowerCase()));

  const createMutation = useMutation({
    mutationFn: (data: Partial<Department>) =>
      employeeService.createDepartment(data as Omit<Department, 'id'>),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setModalOpen(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, ...data }: Partial<Department> & { id: string }) =>
      employeeService.updateDepartment(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setModalOpen(false);
      setEditDept(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => employeeService.deleteDepartment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
    },
  });

  const handleSubmit = (data: Partial<Department>) => {
    if (editDept) {
      updateMutation.mutate({ ...data, id: editDept.id });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (dept: Department) => {
    setEditDept(dept);
    setModalOpen(true);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Department Management</CardTitle>
          <Button
            size="sm"
            onClick={() => {
              setEditDept(null);
              setModalOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Department
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search departments..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Code</TableHead>
                <TableHead className="text-center">Employees</TableHead>
                <TableHead className="text-center">Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="h-24 text-center text-muted-foreground">
                    No departments found
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((dept) => (
                  <TableRow key={dept.id}>
                    <TableCell className="font-medium">{dept.name}</TableCell>
                    <TableCell className="text-muted-foreground">{dept.code}</TableCell>
                    <TableCell className="text-center">{dept.employeeCount}</TableCell>
                    <TableCell className="text-center">
                      <Badge variant={dept.isActive ? 'default' : 'secondary'}>
                        {dept.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleEdit(dept)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => deleteMutation.mutate(dept.id)}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>

        <DepartmentModal
          open={modalOpen}
          onOpenChange={(open) => {
            setModalOpen(open);
            if (!open) setEditDept(null);
          }}
          department={editDept}
          onSubmit={handleSubmit}
          isPending={createMutation.isPending || updateMutation.isPending}
        />
      </CardContent>
    </Card>
  );
}
