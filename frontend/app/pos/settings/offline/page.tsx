// ================================================================
// Offline Settings Page — Task 83
// POS > Settings > Offline
// ================================================================

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { useOfflineStatus } from '@/hooks/useOfflineStatus';
import { useSyncHistory } from '@/hooks/useSyncHistory';
import { useCacheRefresh } from '@/hooks/useCacheRefresh';
import { usePendingCount } from '@/hooks/usePendingCount';
import { ManualSyncButton } from '@/components/pos/offline/ManualSyncButton';
import { CacheRefreshButton } from '@/components/pos/offline/CacheRefreshButton';
import { SyncLogViewer } from '@/components/pos/offline/SyncLogViewer';
import { OfflineIndicator } from '@/components/pos/offline/OfflineIndicator';

// ----------------------------------------------------------------
// Sub-components
// ----------------------------------------------------------------

function ConnectionStatusCard({
  status,
  isOnline,
}: {
  status: string;
  isOnline: boolean;
}) {
  return (
    <div
      className={`p-6 rounded-xl border-2 ${
        isOnline
          ? 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
          : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20'
      }`}
    >
      <div className="flex items-center gap-3">
        <div
          className={`w-4 h-4 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}
        />
        <div>
          <h3 className="font-semibold text-lg">
            {isOnline ? 'Online' : 'Offline'}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Status: {status}
          </p>
        </div>
      </div>
    </div>
  );
}

function CachedDataOverview() {
  const [entities, setEntities] = useState([
    { name: 'Products', count: 0, lastSync: '—' },
    { name: 'Customers', count: 0, lastSync: '—' },
    { name: 'Settings', count: 0, lastSync: '—' },
  ]);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const { idbService } = await import('@/lib/offline/indexeddb');
        const { ObjectStoreNames } = await import('@/lib/offline/schema');
        const stores = [
          { name: 'Products', store: ObjectStoreNames.PRODUCTS },
          { name: 'Customers', store: ObjectStoreNames.CUSTOMERS },
          { name: 'Settings', store: ObjectStoreNames.SETTINGS },
        ];
        const results = await Promise.all(
          stores.map(async (s) => {
            const count = await idbService.count(s.store);
            return { name: s.name, count, lastSync: '—' };
          })
        );
        if (!cancelled) setEntities(results);
      } catch {
        // IndexedDB not available
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="border dark:border-gray-700 rounded-lg overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="text-left px-4 py-2 font-medium">Entity</th>
            <th className="text-left px-4 py-2 font-medium">Cached Count</th>
            <th className="text-left px-4 py-2 font-medium">Last Synced</th>
          </tr>
        </thead>
        <tbody>
          {entities.map((e) => (
            <tr key={e.name} className="border-t dark:border-gray-700">
              <td className="px-4 py-2">{e.name}</td>
              <td className="px-4 py-2 font-mono">{e.count}</td>
              <td className="px-4 py-2 text-gray-500">{e.lastSync}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TroubleshootingSection() {
  const steps = [
    'Check that the server is running and accessible.',
    'Ensure your browser supports IndexedDB and Service Workers.',
    'Try clearing the cache and performing a full sync.',
    'If issues persist, use "Reset Sync State" from the Sync menu.',
    'Contact support if the problem continues.',
  ];

  return (
    <div className="bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
      <h4 className="font-medium mb-2">Troubleshooting</h4>
      <ol className="list-decimal ml-5 text-sm space-y-1 text-gray-700 dark:text-gray-300">
        {steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
    </div>
  );
}

// ----------------------------------------------------------------
// Pending Transactions Section
// ----------------------------------------------------------------

function PendingTransactionsSection() {
  const { total, byStatus, refresh } = usePendingCount();

  return (
    <div className="border dark:border-gray-700 rounded-lg p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-lg" aria-hidden="true">
            📋
          </span>
          <span className="font-medium">Total Pending: {total}</span>
        </div>
        <button
          type="button"
          onClick={refresh}
          className="text-xs text-blue-600 hover:underline"
        >
          Refresh
        </button>
      </div>
      <div className="grid grid-cols-3 gap-3 text-center text-sm">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded p-2">
          <p className="font-mono text-lg font-bold text-yellow-700 dark:text-yellow-400">
            {byStatus.pending}
          </p>
          <p className="text-xs text-gray-500">Pending</p>
        </div>
        <div className="bg-red-50 dark:bg-red-900/20 rounded p-2">
          <p className="font-mono text-lg font-bold text-red-700 dark:text-red-400">
            {byStatus.failed}
          </p>
          <p className="text-xs text-gray-500">Failed</p>
        </div>
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded p-2">
          <p className="font-mono text-lg font-bold text-blue-700 dark:text-blue-400">
            {byStatus.retrying}
          </p>
          <p className="text-xs text-gray-500">Retrying</p>
        </div>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------
// Configuration Section
// ----------------------------------------------------------------

function ConfigurationSection() {
  const [autoSync, setAutoSync] = useState(true);
  const [syncInterval, setSyncInterval] = useState(5);

  return (
    <div className="border dark:border-gray-700 rounded-lg divide-y dark:divide-gray-700">
      <div className="flex items-center justify-between p-4">
        <div>
          <p className="font-medium text-sm">Auto-Sync</p>
          <p className="text-xs text-gray-500">
            Automatically sync when connection is restored
          </p>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={autoSync}
          onClick={() => setAutoSync(!autoSync)}
          className={`w-11 h-6 rounded-full transition-colors relative ${autoSync ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}`}
        >
          <span
            className={`block w-4 h-4 rounded-full bg-white shadow absolute top-1 transition-transform ${autoSync ? 'translate-x-6' : 'translate-x-1'}`}
          />
        </button>
      </div>
      <div className="flex items-center justify-between p-4">
        <div>
          <p className="font-medium text-sm">Sync Interval</p>
          <p className="text-xs text-gray-500">
            How often to auto-sync (minutes)
          </p>
        </div>
        <select
          value={syncInterval}
          onChange={(e) => setSyncInterval(Number(e.target.value))}
          className="border dark:border-gray-600 rounded px-2 py-1 text-sm bg-white dark:bg-gray-800"
        >
          <option value={1}>1 min</option>
          <option value={5}>5 min</option>
          <option value={10}>10 min</option>
          <option value={30}>30 min</option>
        </select>
      </div>
    </div>
  );
}

// ----------------------------------------------------------------
// Data Statistics Section
// ----------------------------------------------------------------

function DataStatisticsSection() {
  const [storageUsed, setStorageUsed] = useState<string>('—');
  const [storageQuota, setStorageQuota] = useState<string>('—');
  const [usagePercent, setUsagePercent] = useState(0);

  useEffect(() => {
    async function load() {
      if (navigator.storage?.estimate) {
        const est = await navigator.storage.estimate();
        const used = est.usage ?? 0;
        const quota = est.quota ?? 0;
        setStorageUsed(formatBytes(used));
        setStorageQuota(formatBytes(quota));
        setUsagePercent(quota > 0 ? Math.round((used / quota) * 100) : 0);
      }
    }
    load();
  }, []);

  return (
    <div className="border dark:border-gray-700 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600 dark:text-gray-400">Storage Used</span>
        <span className="font-mono font-medium">
          {storageUsed} / {storageQuota}
        </span>
      </div>
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all ${usagePercent > 80 ? 'bg-red-500' : usagePercent > 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min(usagePercent, 100)}%` }}
        />
      </div>
      <p className="text-xs text-gray-500">
        {usagePercent}% of available storage used
      </p>
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

// ----------------------------------------------------------------
// Page
// ----------------------------------------------------------------

export default function OfflineSettingsPage() {
  const { status, isOnline, lastSyncTime } = useOfflineStatus();
  const { entries } = useSyncHistory();
  const { lastRefresh } = useCacheRefresh();

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div>
            <h1 className="text-2xl font-bold dark:text-white">
              Offline Settings
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Manage offline data, sync status, and cache configuration.
            </p>
          </div>
          <OfflineIndicator compact />
        </div>
        <div className="flex gap-3">
          <ManualSyncButton variant="primary" />
          <CacheRefreshButton />
        </div>
      </div>

      {lastSyncTime && (
        <p className="text-xs text-gray-400 -mt-4">
          Last synced: {lastSyncTime.toLocaleString()}
        </p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left column */}
        <div className="space-y-8">
          {/* Connection Status */}
          <section aria-label="Connection Status">
            <h2 className="text-lg font-semibold mb-3 dark:text-white">
              Connection
            </h2>
            <ConnectionStatusCard status={status} isOnline={isOnline} />
          </section>

          {/* Pending Transactions */}
          <section aria-label="Pending Transactions">
            <h2 className="text-lg font-semibold mb-3 dark:text-white">
              Pending Transactions
            </h2>
            <PendingTransactionsSection />
          </section>

          {/* Configuration */}
          <section aria-label="Configuration">
            <h2 className="text-lg font-semibold mb-3 dark:text-white">
              Configuration
            </h2>
            <ConfigurationSection />
          </section>
        </div>

        {/* Right column */}
        <div className="space-y-8">
          {/* Cached Data */}
          <section aria-label="Cached Data">
            <h2 className="text-lg font-semibold mb-3 dark:text-white">
              Cached Data
            </h2>
            <CachedDataOverview />
            {lastRefresh && (
              <p className="text-xs text-gray-400 mt-2">
                Cache last refreshed: {lastRefresh.toLocaleString()}
              </p>
            )}
          </section>

          {/* Data Statistics */}
          <section aria-label="Data Statistics">
            <h2 className="text-lg font-semibold mb-3 dark:text-white">
              Storage
            </h2>
            <DataStatisticsSection />
          </section>
        </div>
      </div>

      {/* Sync History — full width */}
      <section aria-label="Sync History">
        <h2 className="text-lg font-semibold mb-3 dark:text-white">
          Sync History
        </h2>
        <SyncLogViewer entries={entries} pageSize={10} />
      </section>

      {/* Troubleshooting */}
      <section aria-label="Troubleshooting">
        <h2 className="text-lg font-semibold mb-3 dark:text-white">Help</h2>
        <TroubleshootingSection />
      </section>
    </div>
  );
}
