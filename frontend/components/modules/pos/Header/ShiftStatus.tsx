'use client';

import { useState, useEffect, useMemo } from 'react';
import {
  CircleDot,
  CirclePause,
  CircleOff,
  ChevronDown,
  DollarSign,
  Receipt,
  Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Badge } from '@/components/ui/badge';
import { usePOS } from '../context/POSContext';
import type { ShiftStatus as ShiftStatusType } from '../types';

function formatDuration(openedAt: string): string {
  const diff = Date.now() - new Date(openedAt).getTime();
  const hours = Math.floor(diff / 3_600_000);
  const minutes = Math.floor((diff % 3_600_000) / 60_000);
  return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;
}

function formatCurrency(amount: number): string {
  return `₨ ${amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}`;
}

const statusConfig: Record<
  ShiftStatusType,
  { icon: typeof CircleDot; color: string; label: string }
> = {
  open: { icon: CircleDot, color: 'text-green-500', label: 'Shift Open' },
  paused: { icon: CirclePause, color: 'text-yellow-500', label: 'Shift Paused' },
  closed: { icon: CircleOff, color: 'text-gray-400', label: 'Shift Closed' },
};

interface ShiftStatusProps {
  compact?: boolean;
}

export function ShiftStatus({ compact = false }: ShiftStatusProps) {
  const { currentShift, openModal } = usePOS();
  const [, setTick] = useState(0);

  // Re-render every minute for duration update
  useEffect(() => {
    if (!currentShift || currentShift.status !== 'open') return;
    const timer = setInterval(() => setTick((t) => t + 1), 60_000);
    return () => clearInterval(timer);
  }, [currentShift]);

  const config = useMemo(() => {
    if (!currentShift) return null;
    return statusConfig[currentShift.status];
  }, [currentShift]);

  if (!currentShift) {
    return (
      <Button variant="outline" size="sm" onClick={() => openModal('shift_open')} className="gap-2">
        <CircleOff className="h-4 w-4 text-gray-400" />
        {!compact && <span>No Active Shift</span>}
        {compact && <span>Open Shift</span>}
      </Button>
    );
  }

  if (!config) return null;
  const StatusIcon = config.icon;

  if (compact) {
    return (
      <div className="flex items-center gap-1.5">
        <StatusIcon className={`h-4 w-4 ${config.color}`} />
        <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
          #{currentShift.sessionNumber}
        </span>
      </div>
    );
  }

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-2">
          <StatusIcon className={`h-4 w-4 ${config.color}`} />
          <span className="font-medium">{config.label}</span>
          <Badge variant="outline" className="text-xs">
            #{currentShift.sessionNumber}
          </Badge>
          <ChevronDown className="h-3 w-3 text-gray-400" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-72" align="center">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold">Shift Details</h4>
            <Badge
              variant={currentShift.status === 'open' ? 'default' : 'secondary'}
              className="text-xs capitalize"
            >
              {currentShift.status}
            </Badge>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
              <span>Cashier</span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {currentShift.cashierName}
              </span>
            </div>
            <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" /> Duration
              </span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {formatDuration(currentShift.openedAt)}
              </span>
            </div>
            <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <DollarSign className="h-3 w-3" /> Opening Cash
              </span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {formatCurrency(currentShift.openingCash)}
              </span>
            </div>
            <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
              <span className="flex items-center gap-1">
                <Receipt className="h-3 w-3" /> Transactions
              </span>
              <span className="font-medium text-gray-900 dark:text-gray-100">
                {currentShift.transactionCount}
              </span>
            </div>
            <div className="flex items-center justify-between text-gray-600 dark:text-gray-400">
              <span>Total Sales</span>
              <span className="font-semibold text-gray-900 dark:text-gray-100">
                {formatCurrency(currentShift.totalSales)}
              </span>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => openModal('shift_close')}
          >
            Close Shift
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
