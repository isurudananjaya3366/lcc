'use client';

import { useState } from 'react';
import { Search, X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const ACTION_OPTIONS = [
  { value: 'all', label: 'All Actions' },
  { value: 'CREATE', label: 'Create' },
  { value: 'UPDATE', label: 'Update' },
  { value: 'DELETE', label: 'Delete' },
  { value: 'LOGIN', label: 'Login' },
  { value: 'LOGOUT', label: 'Logout' },
  { value: 'PERMISSION', label: 'Permission Changes' },
  { value: 'SETTINGS', label: 'Settings Changes' },
];

const ENTITY_OPTIONS = [
  { value: 'all', label: 'All Types' },
  { value: 'Product', label: 'Products' },
  { value: 'User', label: 'Users' },
  { value: 'Order', label: 'Orders' },
  { value: 'Customer', label: 'Customers' },
  { value: 'Inventory', label: 'Inventory' },
  { value: 'Settings', label: 'Settings' },
  { value: 'Role', label: 'Roles' },
  { value: 'Integration', label: 'Integrations' },
];

const DATE_RANGE_OPTIONS = [
  { value: 'today', label: 'Today' },
  { value: '7days', label: 'Last 7 Days' },
  { value: '30days', label: 'Last 30 Days' },
  { value: 'thisMonth', label: 'This Month' },
  { value: 'all', label: 'All Time' },
];

export interface AuditLogFilterState {
  userId?: string;
  action?: string;
  entityType?: string;
  dateRange?: string;
  searchText?: string;
}

const MOCK_USERS = [
  { value: 'all', label: 'All Users' },
  { value: 'u-1', label: 'John Doe' },
  { value: 'u-2', label: 'Jane Smith' },
  { value: 'u-3', label: 'Kamal Perera' },
  { value: 'system', label: 'System' },
];

interface AuditLogFiltersProps {
  filters: AuditLogFilterState;
  onFilterChange: (filters: AuditLogFilterState) => void;
}

export function AuditLogFilters({ filters, onFilterChange }: AuditLogFiltersProps) {
  const [searchValue, setSearchValue] = useState(filters.searchText ?? '');

  const updateFilter = (key: keyof AuditLogFilterState, value: string) => {
    const newFilters = { ...filters };
    if (value === 'all' || value === '') {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    onFilterChange(newFilters);
  };

  const handleSearchChange = (value: string) => {
    setSearchValue(value);
    // Debounced update
    const timeout = setTimeout(() => {
      updateFilter('searchText', value);
    }, 300);
    return () => clearTimeout(timeout);
  };

  const activeFilters = Object.entries(filters).filter(
    ([key, value]) => value && key !== 'searchText'
  );

  const clearAllFilters = () => {
    setSearchValue('');
    onFilterChange({});
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <Select
          value={filters.userId ?? 'all'}
          onValueChange={(val) => updateFilter('userId', val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Users" />
          </SelectTrigger>
          <SelectContent>
            {MOCK_USERS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.action ?? 'all'}
          onValueChange={(val) => updateFilter('action', val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Actions" />
          </SelectTrigger>
          <SelectContent>
            {ACTION_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.entityType ?? 'all'}
          onValueChange={(val) => updateFilter('entityType', val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="All Types" />
          </SelectTrigger>
          <SelectContent>
            {ENTITY_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={filters.dateRange ?? '7days'}
          onValueChange={(val) => updateFilter('dateRange', val)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Last 7 Days" />
          </SelectTrigger>
          <SelectContent>
            {DATE_RANGE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search in details..."
            value={searchValue}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {activeFilters.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {activeFilters.map(([key, value]) => (
            <Badge key={key} variant="secondary" className="gap-1">
              {key}: {value}
              <button
                onClick={() => updateFilter(key as keyof AuditLogFilterState, '')}
                className="ml-1 rounded-full hover:bg-muted"
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
          <Button variant="ghost" size="sm" onClick={clearAllFilters}>
            Clear All
          </Button>
        </div>
      )}
    </div>
  );
}
