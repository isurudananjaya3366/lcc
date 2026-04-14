'use client';

import { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Search, User, Plus } from 'lucide-react';

interface Customer {
  id: string;
  name: string;
  email?: string;
  phone?: string;
}

interface CustomerSelectProps {
  value: string;
  onChange: (value: string) => void;
  error?: string;
}

/**
 * Searchable customer select component with dropdown suggestions.
 * Task 73: Customer Select for Quotes (and reusable in Orders).
 */
export function CustomerSelect({ value, onChange, error }: CustomerSelectProps) {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (search.length < 2) {
      setCustomers([]);
      return;
    }

    setIsLoading(true);
    const timer = setTimeout(async () => {
      try {
        // TODO: Replace with actual customer API call when available
        // e.g., const response = await customerService.search(search);
        // setCustomers(response.results);
        setCustomers([]);
      } catch {
        setCustomers([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  const handleSelect = (customer: Customer) => {
    onChange(customer.id);
    setSearch(customer.name);
    setIsOpen(false);
  };

  return (
    <div ref={containerRef} className="relative space-y-1.5">
      <Label htmlFor="customerSelect">Customer *</Label>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          id="customerSelect"
          placeholder="Search customer by name, email, or phone..."
          value={value && !search ? value : search}
          onChange={(e) => {
            setSearch(e.target.value);
            setIsOpen(true);
            if (!e.target.value) onChange('');
          }}
          onFocus={() => search.length >= 2 && setIsOpen(true)}
          className="pl-9"
        />
      </div>

      {/* Dropdown */}
      {isOpen && (search.length >= 2 || customers.length > 0) && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-white shadow-lg dark:bg-gray-900">
          {isLoading ? (
            <div className="p-3 text-center text-sm text-gray-500">Searching...</div>
          ) : customers.length > 0 ? (
            <ul className="max-h-48 overflow-auto py-1">
              {customers.map((customer) => (
                <li key={customer.id}>
                  <button
                    type="button"
                    className="flex w-full items-center gap-3 px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-800"
                    onClick={() => handleSelect(customer)}
                  >
                    <User className="h-4 w-4 text-gray-400" />
                    <div>
                      <p className="font-medium">{customer.name}</p>
                      {customer.email && <p className="text-xs text-gray-500">{customer.email}</p>}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="p-3 text-center text-sm text-gray-500">
              No customers found
              <Button
                type="button"
                variant="link"
                size="sm"
                className="ml-1"
                onClick={() => {
                  // TODO: Open create customer modal when available
                  setIsOpen(false);
                }}
              >
                <Plus className="mr-1 h-3 w-3" />
                Create New
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Direct ID fallback input */}
      {!customers.length && <Input type="hidden" value={value} />}

      {/* Manual ID input when no customer API */}
      {search === '' && !value && (
        <Input
          placeholder="Or enter customer ID directly"
          onChange={(e) => onChange(e.target.value)}
          className="mt-1 text-xs"
        />
      )}

      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
