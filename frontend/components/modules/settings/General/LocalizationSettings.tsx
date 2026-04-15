'use client';

import { SettingsSectionCard } from './SettingsSectionCard';
import { TimezoneSelect } from './TimezoneSelect';
import { CurrencySelect } from './CurrencySelect';
import { DateFormatSelect } from './DateFormatSelect';

interface LocalizationSettingsProps {
  timezone: string;
  currency: string;
  dateFormat: string;
  onTimezoneChange: (value: string) => void;
  onCurrencyChange: (value: string) => void;
  onDateFormatChange: (value: string) => void;
}

export function LocalizationSettings({
  timezone,
  currency,
  dateFormat,
  onTimezoneChange,
  onCurrencyChange,
  onDateFormatChange,
}: LocalizationSettingsProps) {
  return (
    <SettingsSectionCard
      title="Localization"
      description="Configure your region, currency, and display preferences."
    >
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <TimezoneSelect value={timezone} onChange={onTimezoneChange} />
        <CurrencySelect value={currency} onChange={onCurrencyChange} />
        <DateFormatSelect value={dateFormat} onChange={onDateFormatChange} />
      </div>
    </SettingsSectionCard>
  );
}
