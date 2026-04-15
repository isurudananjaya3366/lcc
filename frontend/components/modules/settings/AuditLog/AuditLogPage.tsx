'use client';

import { useState, useMemo } from 'react';
import { AuditLogFilters, type AuditLogFilterState } from './AuditLogFilters';
import { AuditLogTable } from './AuditLogTable';
import type { AuditLogEntry } from '@/types/settings';

// Mock data for UI development
const MOCK_ENTRIES: AuditLogEntry[] = [
  {
    id: 'al-1',
    timestamp: new Date(Date.now() - 2 * 60000).toISOString(),
    userId: 'u-1',
    userName: 'John Doe',
    action: 'UPDATE',
    entity: 'Product',
    entityId: 'prod-123',
    details: 'Updated product name from "Widget A" to "Widget A - Premium"',
    ipAddress: '192.168.1.10',
  },
  {
    id: 'al-2',
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    userId: 'u-2',
    userName: 'Jane Smith',
    action: 'CREATE',
    entity: 'User',
    entityId: 'u-5',
    details: 'Created new user account for alex@example.com',
    ipAddress: '192.168.1.15',
  },
  {
    id: 'al-3',
    timestamp: new Date(Date.now() - 60 * 60000).toISOString(),
    userId: 'u-1',
    userName: 'Admin',
    action: 'PERMISSION',
    entity: 'Role',
    entityId: 'role-3',
    details: 'Modified permissions for "Sales Manager" role',
    ipAddress: '192.168.1.1',
  },
  {
    id: 'al-4',
    timestamp: new Date(Date.now() - 2 * 3600000).toISOString(),
    userId: 'system',
    userName: 'System',
    action: 'SYSTEM',
    entity: 'Settings',
    details: 'Automated backup completed successfully',
  },
  {
    id: 'al-5',
    timestamp: new Date(Date.now() - 3 * 3600000).toISOString(),
    userId: 'u-3',
    userName: 'Kamal Perera',
    action: 'DELETE',
    entity: 'Product',
    entityId: 'prod-456',
    details: 'Deleted product "Discontinued Item X"',
    ipAddress: '10.0.0.5',
  },
  {
    id: 'al-6',
    timestamp: new Date(Date.now() - 4 * 3600000).toISOString(),
    userId: 'u-2',
    userName: 'Jane Smith',
    action: 'LOGIN',
    entity: 'User',
    entityId: 'u-2',
    details: 'User logged in via email/password',
    ipAddress: '192.168.1.15',
  },
  {
    id: 'al-7',
    timestamp: new Date(Date.now() - 5 * 3600000).toISOString(),
    userId: 'u-1',
    userName: 'Admin',
    action: 'SETTINGS',
    entity: 'Settings',
    details: 'Updated company timezone from UTC to Asia/Colombo',
    ipAddress: '192.168.1.1',
  },
  {
    id: 'al-8',
    timestamp: new Date(Date.now() - 24 * 3600000).toISOString(),
    userId: 'u-3',
    userName: 'Kamal Perera',
    action: 'LOGOUT',
    entity: 'User',
    entityId: 'u-3',
    details: 'User logged out',
    ipAddress: '10.0.0.5',
  },
  {
    id: 'al-9',
    timestamp: new Date(Date.now() - 48 * 3600000).toISOString(),
    userId: 'u-1',
    userName: 'Admin',
    action: 'CREATE',
    entity: 'Integration',
    entityId: 'int-1',
    details: 'Connected PayHere payment gateway integration',
    ipAddress: '192.168.1.1',
  },
  {
    id: 'al-10',
    timestamp: new Date(Date.now() - 72 * 3600000).toISOString(),
    userId: 'u-2',
    userName: 'Jane Smith',
    action: 'UPDATE',
    entity: 'Order',
    entityId: 'ord-789',
    details: 'Updated order status from "Processing" to "Shipped"',
    ipAddress: '192.168.1.15',
  },
];

export function AuditLogPage() {
  const [filters, setFilters] = useState<AuditLogFilterState>({});

  const filteredEntries = useMemo(() => {
    return MOCK_ENTRIES.filter((entry) => {
      if (filters.action && entry.action !== filters.action) return false;
      if (filters.entityType && entry.entity !== filters.entityType) return false;
      if (filters.searchText) {
        const search = filters.searchText.toLowerCase();
        return (
          entry.details.toLowerCase().includes(search) ||
          entry.userName.toLowerCase().includes(search) ||
          entry.entity.toLowerCase().includes(search)
        );
      }
      return true;
    });
  }, [filters]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Audit Log</h1>
        <p className="text-muted-foreground">
          Track all system activities and changes.
        </p>
      </div>

      <AuditLogFilters filters={filters} onFilterChange={setFilters} />
      <AuditLogTable entries={filteredEntries} />
    </div>
  );
}
