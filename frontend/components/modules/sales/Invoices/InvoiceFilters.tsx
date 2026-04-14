'use client';

import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export interface InvoiceFilterValues {
  search: string;
  status: string;
  dateRange: string;
}

interface InvoiceFiltersProps {
  filters: InvoiceFilterValues;
  onFiltersChange: (filters: InvoiceFilterValues) => void;
}

export function InvoiceFilters({ filters, onFiltersChange }: InvoiceFiltersProps) {
  const hasActiveFilters =
    filters.search || filters.status !== 'all' || filters.dateRange !== 'all';

  const clearFilters = () => {
    onFiltersChange({ search: '', status: 'all', dateRange: 'all' });
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          placeholder="Search by invoice #, customer..."
          value={filters.search}
          onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
          className="pl-10"
        />
        {filters.search && (
          <button
            onClick={() => onFiltersChange({ ...filters, search: '' })}
            className="absolute right-3 top-1/2 -translate-y-1/2"
          >
            <X className="h-4 w-4 text-gray-400 hover:text-gray-600" />
          </button>
        )}
      </div>

      <Select
        value={filters.status}
        onValueChange={(value) => onFiltersChange({ ...filters, status: value })}
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          <SelectItem value="draft">Draft</SelectItem>
          <SelectItem value="sent">Sent</SelectItem>
          <SelectItem value="paid">Paid</SelectItem>
          <SelectItem value="partially_paid">Partial</SelectItem>
          <SelectItem value="overdue">Overdue</SelectItem>
          <SelectItem value="void">Void</SelectItem>
          <SelectItem value="cancelled">Cancelled</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={filters.dateRange}
        onValueChange={(value) => onFiltersChange({ ...filters, dateRange: value })}
      >
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Date Range" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Time</SelectItem>
          <SelectItem value="this_month">This Month</SelectItem>
          <SelectItem value="last_month">Last Month</SelectItem>
          <SelectItem value="this_quarter">This Quarter</SelectItem>
          <SelectItem value="this_year">This Year</SelectItem>
        </SelectContent>
      </Select>

      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={clearFilters}>
          <X className="mr-1 h-4 w-4" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}
