'use client';

import { WelcomeBanner } from './WelcomeBanner';
import { KPISummary } from './KPISummary';
import { SalesKPI } from './SalesKPI';
import { OrdersKPI } from './OrdersKPI';
import { LowStockAlert } from './LowStockAlert';
import { PendingTasks } from './PendingTasks';
import { DashboardQuickActions } from './QuickActions';
import { ActivityFeed } from './ActivityFeed';
import { SalesChart } from './SalesChart';

/**
 * DashboardHome — Assembled dashboard landing page.
 *
 * Uses mock data by default. When the backend endpoints are available,
 * wire up the useKPIData / useActivityFeed / useSalesChartData hooks.
 */
export function DashboardHome() {
  return (
    <div className="space-y-6">
      {/* Welcome banner */}
      <WelcomeBanner />

      {/* KPI summary cards */}
      <KPISummary>
        <SalesKPI todaySales={124500} yesterdaySales={98200} />
        <OrdersKPI todayOrders={42} yesterdayOrders={35} />
        <LowStockAlert lowStockCount={12} criticalCount={3} />
        <PendingTasks pendingCount={7} />
      </KPISummary>

      {/* Quick actions */}
      <section aria-labelledby="quick-actions-heading">
        <h2
          id="quick-actions-heading"
          className="mb-3 text-lg font-semibold text-gray-900 dark:text-gray-100"
        >
          Quick Actions
        </h2>
        <DashboardQuickActions />
      </section>

      {/* Two-column layout: chart + activity feed */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section
          className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800 lg:col-span-2"
          aria-labelledby="sales-chart-heading"
        >
          <h2
            id="sales-chart-heading"
            className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100"
          >
            Sales Overview
          </h2>
          <SalesChart />
        </section>

        <section
          className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800"
          aria-labelledby="activity-feed-heading"
        >
          <h2
            id="activity-feed-heading"
            className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100"
          >
            Recent Activity
          </h2>
          <ActivityFeed />
        </section>
      </div>
    </div>
  );
}
