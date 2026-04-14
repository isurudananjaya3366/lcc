'use client';

import { useCallback, useMemo, useState } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { cn } from '@/lib/cn';

// ─── Types ──────────────────────────────────────────────────────

type TimePeriod = '7d' | '30d' | 'this_month' | 'last_month';

interface ChartDataPoint {
  date: string;
  sales: number;
}

interface SalesChartProps {
  data?: ChartDataPoint[];
  isLoading?: boolean;
}

// ─── Mock Data Generator ────────────────────────────────────────

function generateMockData(period: TimePeriod): ChartDataPoint[] {
  const points: ChartDataPoint[] = [];
  const now = new Date();
  let days: number;

  switch (period) {
    case '7d':
      days = 7;
      break;
    case '30d':
    case 'this_month':
      days = 30;
      break;
    case 'last_month':
      days = 30;
      break;
  }

  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    points.push({
      date: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      sales: Math.floor(Math.random() * 80_000) + 20_000,
    });
  }

  return points;
}

// ─── Currency Formatter ─────────────────────────────────────────

function formatCurrency(val: number): string {
  if (val >= 1_000_000) return `${(val / 1_000_000).toFixed(1)}M`;
  if (val >= 1_000) return `${(val / 1_000).toFixed(0)}K`;
  return val.toLocaleString();
}

// ─── Period Options ─────────────────────────────────────────────

const periodOptions: { value: TimePeriod; label: string }[] = [
  { value: '7d', label: '7 Days' },
  { value: '30d', label: '30 Days' },
  { value: 'this_month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
];

// ─── Component ──────────────────────────────────────────────────

export function SalesChart({ data, isLoading }: SalesChartProps) {
  const [period, setPeriod] = useState<TimePeriod>('7d');

  const chartData = useMemo(() => data ?? generateMockData(period), [data, period]);

  const handlePeriodChange = useCallback((p: TimePeriod) => {
    setPeriod(p);
  }, []);

  if (isLoading) {
    return <div className="h-[300px] animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />;
  }

  return (
    <div>
      {/* Period selector */}
      <div className="mb-4 flex flex-wrap gap-1">
        {periodOptions.map((opt) => (
          <button
            key={opt.value}
            type="button"
            onClick={() => handlePeriodChange(opt.value)}
            className={cn(
              'rounded-lg px-3 py-1.5 text-xs font-medium transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
              period === opt.value
                ? 'bg-primary text-white'
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
            )}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
          <defs>
            <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} />
          <YAxis
            tickFormatter={(val: number) => formatCurrency(val)}
            tick={{ fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            width={55}
          />
          <Tooltip
            formatter={(val: number) => [`LKR ${val.toLocaleString()}`, 'Sales']}
            contentStyle={{
              borderRadius: 8,
              border: '1px solid #e5e7eb',
              fontSize: 12,
            }}
          />
          <Area
            type="monotone"
            dataKey="sales"
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            fill="url(#salesGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
