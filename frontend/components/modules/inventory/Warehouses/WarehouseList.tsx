'use client';

import { useState } from 'react';
import { useWarehouses } from '@/hooks/queries/useWarehouses';

import { WarehousesHeader } from './WarehousesHeader';
import { WarehouseCards } from './WarehouseCards';

export function WarehouseList() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading } = useWarehouses();
  const warehouses = data?.data ?? [];

  const filtered = searchQuery
    ? warehouses.filter(
        (wh) =>
          wh.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          wh.code.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : warehouses;

  const activeCount = warehouses.filter((wh) => wh.isActive).length;

  return (
    <div className="space-y-6">
      <WarehousesHeader
        count={warehouses.length}
        activeCount={activeCount}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <WarehouseCards warehouses={filtered} isLoading={isLoading} />
    </div>
  );
}
