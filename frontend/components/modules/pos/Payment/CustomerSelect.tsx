'use client';

import { useState, useEffect } from 'react';
import { Search, X, User } from 'lucide-react';
import { useDebounce } from '@/hooks/useDebounce';
import { posService } from '@/services/pos';
import type { POSCustomer } from '../types';

interface CustomerSelectProps {
  customer: POSCustomer | null;
  onSelect: (customer: POSCustomer | null) => void;
}

export function CustomerSelect({ customer, onSelect }: CustomerSelectProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<POSCustomer[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults([]);
      return;
    }
    setIsSearching(true);
    posService
      .searchCustomers(debouncedQuery)
      .then(setResults)
      .catch(() => setResults([]))
      .finally(() => setIsSearching(false));
  }, [debouncedQuery]);

  if (customer) {
    return (
      <div className="flex items-center justify-between rounded-md border border-green-200 bg-green-50 px-3 py-2 dark:border-green-800 dark:bg-green-950">
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-green-600" />
          <div>
            <p className="text-sm font-medium text-green-800 dark:text-green-200">
              {customer.name}
            </p>
            {customer.phone && (
              <p className="text-xs text-green-600 dark:text-green-400">{customer.phone}</p>
            )}
          </div>
        </div>
        <button
          onClick={() => onSelect(null)}
          className="rounded p-1 text-green-400 hover:text-green-600"
          aria-label="Remove customer"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    );
  }

  if (!showSearch) {
    return (
      <button
        onClick={() => setShowSearch(true)}
        className="flex w-full items-center gap-2 rounded-md border border-dashed border-gray-300 px-3 py-2 text-sm text-gray-500 transition-colors hover:border-gray-400 hover:text-gray-700 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:text-gray-300"
      >
        <User className="h-4 w-4" />
        Attach Customer (optional)
      </button>
    );
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search customer by name or phone..."
          className="w-full rounded-md border border-gray-300 py-2 pl-9 pr-8 text-sm dark:border-gray-600 dark:bg-gray-800"
          // eslint-disable-next-line jsx-a11y/no-autofocus
          autoFocus
        />
        <button
          onClick={() => {
            setShowSearch(false);
            setQuery('');
          }}
          className="absolute right-2 top-2 rounded p-0.5 text-gray-400 hover:text-gray-600"
          aria-label="Close search"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {(results.length > 0 || isSearching) && (
        <div className="absolute z-10 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800">
          {isSearching ? (
            <p className="px-3 py-2 text-sm text-gray-400">Searching...</p>
          ) : (
            results.map((c) => (
              <button
                key={c.id}
                onClick={() => {
                  onSelect(c);
                  setShowSearch(false);
                  setQuery('');
                }}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <User className="h-4 w-4 text-gray-400" />
                <div>
                  <p className="font-medium">{c.name}</p>
                  {c.phone && <p className="text-xs text-gray-400">{c.phone}</p>}
                </div>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
