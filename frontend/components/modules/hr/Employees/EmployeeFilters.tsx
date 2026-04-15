'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, X } from 'lucide-react';
import { DepartmentFilter } from './DepartmentFilter';
import { StatusFilter } from './StatusFilter';
import { ViewToggle } from './ViewToggle';

export interface EmployeeFilterState {
  search: string;
  department: string;
  status: string;
}

interface EmployeeFiltersProps {
  filters: EmployeeFilterState;
  onFiltersChange: (filters: EmployeeFilterState) => void;
  viewMode: 'cards' | 'table';
  onViewModeChange: (mode: 'cards' | 'table') => void;
}

export function EmployeeFilters({
  filters,
  onFiltersChange,
  viewMode,
  onViewModeChange,
}: EmployeeFiltersProps) {
  const [searchTerm, setSearchTerm] = useState(filters.search);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== filters.search) {
        onFiltersChange({ ...filters, search: searchTerm });
      }
    }, 300);
    return () => clearTimeout(timer);
  }, [searchTerm, filters, onFiltersChange]);

  const hasActiveFilters =
    filters.search || filters.department !== 'all' || filters.status !== 'all';

  const clearFilters = () => {
    setSearchTerm('');
    onFiltersChange({ search: '', department: 'all', status: 'all' });
  };

  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex flex-1 items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search employees..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        <DepartmentFilter
          value={filters.department}
          onChange={(department) => onFiltersChange({ ...filters, department })}
        />
        <StatusFilter
          value={filters.status}
          onChange={(status) => onFiltersChange({ ...filters, status })}
        />
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="mr-1 h-4 w-4" />
            Clear
          </Button>
        )}
      </div>
      <ViewToggle viewMode={viewMode} onViewModeChange={onViewModeChange} />
    </div>
  );
}
