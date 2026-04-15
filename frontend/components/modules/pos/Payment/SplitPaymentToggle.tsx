'use client';

import { Switch } from '@/components/ui/switch';

interface SplitPaymentToggleProps {
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export function SplitPaymentToggle({ enabled, onToggle }: SplitPaymentToggleProps) {
  return (
    <div className="flex items-center justify-between">
      <label
        htmlFor="split-toggle"
        className="text-sm font-medium text-gray-700 dark:text-gray-300"
      >
        Split Payment
      </label>
      <Switch id="split-toggle" checked={enabled} onCheckedChange={onToggle} />
    </div>
  );
}
