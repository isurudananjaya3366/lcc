'use client';

import { useState, useCallback } from 'react';
import { useEmployees, useDepartments, useDeleteEmployee } from '@/hooks/hr/useEmployees';
import { EmployeesHeader } from './EmployeesHeader';
import { EmployeeSummaryCards } from './EmployeeSummaryCards';
import { EmployeeFilters, type EmployeeFilterState } from './EmployeeFilters';
import { EmployeeCardsGrid } from './EmployeeCardsGrid';
import { EmployeesTable } from './EmployeesTable';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';

const PAGE_SIZE = 12;

export function EmployeesList() {
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [filters, setFilters] = useState<EmployeeFilterState>({
    search: '',
    department: 'all',
    status: 'all',
  });
  const [page, setPage] = useState(1);

  const queryFilters = {
    search: filters.search || undefined,
    department: filters.department !== 'all' ? filters.department : undefined,
    status: filters.status !== 'all' ? filters.status : undefined,
  };

  const { data, isLoading } = useEmployees({
    ...queryFilters,
    page: String(page),
    pageSize: String(PAGE_SIZE),
  } as never);
  const { data: departmentsResponse } = useDepartments();
  const deleteMutation = useDeleteEmployee();

  const employees = data?.data ?? [];
  const pagination = data?.pagination;
  const departments = departmentsResponse?.data ?? [];

  const handleFiltersChange = useCallback((newFilters: EmployeeFilterState) => {
    setFilters(newFilters);
    setPage(1);
  }, []);

  const handleDelete = useCallback(
    (id: string) => {
      if (window.confirm('Are you sure you want to delete this employee?')) {
        deleteMutation.mutate(id);
      }
    },
    [deleteMutation]
  );

  return (
    <div className="space-y-6">
      <EmployeesHeader />

      <EmployeeSummaryCards employees={employees} departments={departments} />

      <EmployeeFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        viewMode={viewMode}
        onViewModeChange={setViewMode}
      />

      {isLoading ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      ) : viewMode === 'cards' ? (
        <EmployeeCardsGrid employees={employees} onDelete={handleDelete} />
      ) : (
        <EmployeesTable employees={employees} onDelete={handleDelete} />
      )}

      {pagination && pagination.totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Showing {(page - 1) * PAGE_SIZE + 1} to{' '}
            {Math.min(page * PAGE_SIZE, pagination.totalCount)} of {pagination.totalCount} employees
          </p>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.hasPrevious}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="mr-1 h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">
              Page {page} of {pagination.totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.hasNext}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
