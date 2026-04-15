'use client';

import { useState, useEffect, useRef } from 'react';
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

interface VendorFiltersProps {
  onFiltersChange: (filters: { search?: string; status?: string; category?: string }) => void;
}

export function VendorFilters({ onFiltersChange }: VendorFiltersProps) {
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('all');
  const [category, setCategory] = useState('all');
  const debounceRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      onFiltersChange({
        search: search || undefined,
        status: status === 'all' ? undefined : status,
        category: category === 'all' ? undefined : category,
      });
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [search, status, category, onFiltersChange]);

  const activeCount = [
    search,
    status !== 'all' ? status : '',
    category !== 'all' ? category : '',
  ].filter(Boolean).length;

  function clearFilters() {
    setSearch('');
    setStatus('all');
    setCategory('all');
  }

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <div className="relative flex-1 min-w-[200px] max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search vendors..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9 pr-8"
        />
        {search && (
          <button
            onClick={() => setSearch('')}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <Select value={status} onValueChange={setStatus}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Status</SelectItem>
          <SelectItem value="ACTIVE">Active</SelectItem>
          <SelectItem value="INACTIVE">Inactive</SelectItem>
        </SelectContent>
      </Select>

      <Select value={category} onValueChange={setCategory}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Category" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Categories</SelectItem>
          <SelectItem value="RAW_MATERIALS">Raw Materials</SelectItem>
          <SelectItem value="FINISHED_GOODS">Finished Goods</SelectItem>
          <SelectItem value="SERVICES">Services</SelectItem>
          <SelectItem value="EQUIPMENT">Equipment</SelectItem>
          <SelectItem value="UTILITIES">Utilities</SelectItem>
        </SelectContent>
      </Select>

      {activeCount > 0 && (
        <Button variant="ghost" size="sm" onClick={clearFilters}>
          Clear ({activeCount})
        </Button>
      )}
    </div>
  );
}
