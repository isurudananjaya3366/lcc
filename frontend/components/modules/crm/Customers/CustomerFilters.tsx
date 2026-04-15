'use client';

import { useRef, useCallback, useEffect, useState } from 'react';
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

interface CustomerFiltersProps {
  currentFilters: {
    search: string;
    status: string;
    type: string;
    creditStatus: string;
  };
  onSearchChange: (query: string) => void;
  onStatusChange: (status: string) => void;
  onTypeChange: (type: string) => void;
  onCreditChange: (credit: string) => void;
}

export function CustomerFilters({
  currentFilters,
  onSearchChange,
  onStatusChange,
  onTypeChange,
  onCreditChange,
}: CustomerFiltersProps) {
  const [localSearch, setLocalSearch] = useState(currentFilters.search);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const handleSearch = useCallback(
    (value: string) => {
      setLocalSearch(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        onSearchChange(value);
      }, 300);
    },
    [onSearchChange]
  );

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const activeCount = [
    currentFilters.search,
    currentFilters.status,
    currentFilters.type,
    currentFilters.creditStatus,
  ].filter(Boolean).length;

  const clearAll = () => {
    setLocalSearch('');
    onSearchChange('');
    onStatusChange('');
    onTypeChange('');
    onCreditChange('');
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="relative w-64">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search customers..."
          value={localSearch}
          onChange={(e) => handleSearch(e.target.value)}
          className="pl-9 pr-8"
        />
        {localSearch && (
          <button
            onClick={() => handleSearch('')}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <Select value={currentFilters.status} onValueChange={onStatusChange}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Statuses</SelectItem>
          <SelectItem value="ACTIVE">Active</SelectItem>
          <SelectItem value="INACTIVE">Inactive</SelectItem>
        </SelectContent>
      </Select>

      <Select value={currentFilters.type} onValueChange={onTypeChange}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Types</SelectItem>
          <SelectItem value="INDIVIDUAL">Individual</SelectItem>
          <SelectItem value="BUSINESS">Business</SelectItem>
          <SelectItem value="WHOLESALER">Wholesale</SelectItem>
        </SelectContent>
      </Select>

      <Select value={currentFilters.creditStatus} onValueChange={onCreditChange}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Credit Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Credit</SelectItem>
          <SelectItem value="GOOD">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              Good Standing
            </span>
          </SelectItem>
          <SelectItem value="OVERDUE">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-yellow-500" />
              Overdue
            </span>
          </SelectItem>
          <SelectItem value="EXCEEDED">
            <span className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              Exceeded
            </span>
          </SelectItem>
        </SelectContent>
      </Select>

      {activeCount > 0 && (
        <Button variant="ghost" size="sm" onClick={clearAll}>
          Clear filters ({activeCount})
        </Button>
      )}
    </div>
  );
}
