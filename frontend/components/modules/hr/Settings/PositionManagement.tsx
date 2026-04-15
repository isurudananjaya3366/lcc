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
import { PositionModal } from './PositionModal';
import { usePositions } from '@/hooks/hr/useEmployees';
import employeeService from '@/services/api/employeeService';
import type { Position } from '@/types/hr';

export function PositionManagement() {
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editPos, setEditPos] = useState<Position | null>(null);
  const queryClient = useQueryClient();

  const { data, isLoading } = usePositions();
  const positions = data?.data ?? [];

  const filtered = positions.filter((p) => p.title.toLowerCase().includes(search.toLowerCase()));

  const createMutation = useMutation({
    mutationFn: (data: Partial<Position>) =>
      employeeService.createPosition(data as Omit<Position, 'id'>),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      setModalOpen(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, ...data }: Partial<Position> & { id: string }) =>
      employeeService.updatePosition(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
      setModalOpen(false);
      setEditPos(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => employeeService.deletePosition(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions'] });
    },
  });

  const handleSubmit = (data: Partial<Position>) => {
    if (editPos) {
      updateMutation.mutate({ ...data, id: editPos.id });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleEdit = (pos: Position) => {
    setEditPos(pos);
    setModalOpen(true);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Position Management</CardTitle>
          <Button
            size="sm"
            onClick={() => {
              setEditPos(null);
              setModalOpen(true);
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Add Position
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search positions..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Code</TableHead>
                <TableHead>Department</TableHead>
                <TableHead>Level</TableHead>
                <TableHead className="text-center">Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center">
                    Loading...
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                    No positions found
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map((pos) => (
                  <TableRow key={pos.id}>
                    <TableCell className="font-medium">{pos.title}</TableCell>
                    <TableCell className="text-muted-foreground">{pos.code}</TableCell>
                    <TableCell>{pos.departmentId}</TableCell>
                    <TableCell>{pos.level ?? '—'}</TableCell>
                    <TableCell className="text-center">
                      <Badge variant={pos.isActive ? 'default' : 'secondary'}>
                        {pos.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleEdit(pos)}>
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => deleteMutation.mutate(pos.id)}
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

        <PositionModal
          open={modalOpen}
          onOpenChange={(open) => {
            setModalOpen(open);
            if (!open) setEditPos(null);
          }}
          position={editPos}
          onSubmit={handleSubmit}
          isPending={createMutation.isPending || updateMutation.isPending}
        />
      </CardContent>
    </Card>
  );
}
