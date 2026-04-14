'use client';

import { useState, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';

interface OrderFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  statusFilter?: string;
  onStatusChange?: (value: string) => void;
}

export function OrderFilters({
  search,
  onSearchChange,
  statusFilter,
  onStatusChange,
}: OrderFiltersProps) {
  const [paymentStatus, setPaymentStatus] = useState<string>('all');
  const [dateRange, setDateRange] = useState<string>('all');
  const [debouncedSearch, setDebouncedSearch] = useState(search);

  // Debounce search input (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearchChange(debouncedSearch);
    }, 300);
    return () => clearTimeout(timer);
  }, [debouncedSearch, onSearchChange]);

  const currentStatus = statusFilter ?? 'all';

  const hasActiveFilters =
    search || currentStatus !== 'all' || paymentStatus !== 'all' || dateRange !== 'all';

  const clearFilters = () => {
    setDebouncedSearch('');
    onSearchChange('');
    onStatusChange?.('all');
    setPaymentStatus('all');
    setDateRange('all');
  };

  return (
    <div className="flex flex-wrap items-center gap-4">
      {/* Search */}
      <div className="relative w-full max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          placeholder="Search orders..."
          value={debouncedSearch}
          onChange={(e) => setDebouncedSearch(e.target.value)}
          className="pl-9 pr-8"
        />
        {debouncedSearch && (
          <button
            type="button"
            onClick={() => {
              setDebouncedSearch('');
              onSearchChange('');
            }}
            className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Order Status */}
      {onStatusChange && (
        <Select value={currentStatus} onValueChange={onStatusChange}>
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="DRAFT">Draft</SelectItem>
            <SelectItem value="PENDING">Pending</SelectItem>
            <SelectItem value="CONFIRMED">Confirmed</SelectItem>
            <SelectItem value="PROCESSING">Processing</SelectItem>
            <SelectItem value="SHIPPED">Shipped</SelectItem>
            <SelectItem value="DELIVERED">Delivered</SelectItem>
            <SelectItem value="COMPLETED">Completed</SelectItem>
            <SelectItem value="CANCELLED">Cancelled</SelectItem>
            <SelectItem value="REFUNDED">Refunded</SelectItem>
          </SelectContent>
        </Select>
      )}

      {/* Payment Status */}
      <Select value={paymentStatus} onValueChange={setPaymentStatus}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Payment Status" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Payments</SelectItem>
          <SelectItem value="UNPAID">Unpaid</SelectItem>
          <SelectItem value="PARTIAL">Partial</SelectItem>
          <SelectItem value="PAID">Paid</SelectItem>
          <SelectItem value="OVERPAID">Overpaid</SelectItem>
          <SelectItem value="REFUNDED">Refunded</SelectItem>
        </SelectContent>
      </Select>

      {/* Date Range */}
      <Select value={dateRange} onValueChange={setDateRange}>
        <SelectTrigger className="w-[160px]">
          <SelectValue placeholder="Date Range" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Time</SelectItem>
          <SelectItem value="today">Today</SelectItem>
          <SelectItem value="yesterday">Yesterday</SelectItem>
          <SelectItem value="week">This Week</SelectItem>
          <SelectItem value="month">This Month</SelectItem>
          <SelectItem value="quarter">This Quarter</SelectItem>
        </SelectContent>
      </Select>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <Button variant="ghost" size="sm" onClick={clearFilters}>
          <X className="mr-1 h-4 w-4" />
          Clear Filters
        </Button>
      )}
    </div>
  );
}
